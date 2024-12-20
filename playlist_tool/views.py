from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.conf import settings
from django.core.paginator import Paginator
from django.middleware.csrf import get_token
from django.utils.http import urlencode
from .models import Artist, SpotifyProfile, Playlist, Track

import base64
import logging
import random
import requests

logger = logging.getLogger(__name__)

def index(request):
    access_token = request.session.get("access_token")
    return render(request, "playlist_tool/index.html", {"access_token": access_token})

def spotify_login(request):
    if not settings.SPOTIFY_CLIENT_ID or not settings.SPOTIFY_REDIRECT_URI:
        logger.error("Spotify Client ID or Redirect URI is not configured.")
        return JsonResponse({"error": "Interval server error."}, status=500)
    
    auth_url = "https://accounts.spotify.com/authorize?"
    csrf_token = get_token(request)
    request.session["spotify_csrf_token"] = csrf_token
    params = {
        "response_type": "code",
        "client_id": settings.SPOTIFY_CLIENT_ID,
        "scope": "user-read-private user-read-email playlist-read-private user-top-read",
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "state": csrf_token,
    }
    url = f"{auth_url}{urlencode(params)}"
    
    return redirect(url)

def spotify_callback(request):
    code = request.GET.get("code")
    error = request.GET.get("error")
    state = request.GET.get("state")
    
    if error:
        logger.error(f"Spotify authorization failed with error: {error}")
        return JsonResponse({"error": f"Authorization failed."}, status=400)
    
    session_csrf_token = request.session.get("spotify_csrf_token")
    
    if not session_csrf_token:
        logger.error("CSRF token not found in the session.")
        return JsonResponse({"error": "Invalid session."}, status=400)
    
    if state != session_csrf_token:
        logger.warning(f"CSRF token mismatch. Expected: {session_csrf_token}, received: {state}")
        return JsonResponse({"error": "Invalid request."}, status=400)
    
    token_url = "https://accounts.spotify.com/api/token"
    form = {
        "code": code,
        "redirect_uri": settings.SPOTIFY_REDIRECT_URI,
        "grant_type": "authorization_code"
    }
    
    encoded_credentials = base64.b64encode(f"{settings.SPOTIFY_CLIENT_ID}:{settings.SPOTIFY_CLIENT_SECRET}".encode()).decode()
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Authorization": f"Basic {encoded_credentials}",
    }
    
    try:
        response = requests.post(token_url, data=form, headers=headers)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        logger.error(f"Failed to exchange code for tokens: {e}")
        return JsonResponse({"error": "Failed to authenticate with Spotify."}, status=500)
    
    tokens = response.json()
    access_token = tokens.get("access_token")
    refresh_token = tokens.get("refresh_token")
    expires_in = tokens.get("expires_in")
    
    if not access_token:
        logger.error("Spotify token exchange did not return an access token.")
        return JsonResponse({"error": "Authentication failed."}, status=500)
    
    request.session["access_token"] = access_token
    request.session["refresh_token"] = refresh_token
    request.session["expires_in"] = expires_in
    
    logger.info("User successfully authenticated with Spotify.")
    
    return redirect("playlist_tool:index")
    
def spotify_logout(request):
    request.session.flush()
    return redirect("playlist_tool:index")

def profile(request):
    access_token = request.session.get("access_token")
    if not access_token:
        logger.warning("No access token found in session. Redirecting to Spotify login.")
        return redirect("playlist_tool:spotify_login")
    
    profile_url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(profile_url, headers=headers)
    
    if response.status_code != 200:
        logger.error(f"Failed to fetch Spotify profile. Status code: {response.status_code}")
        return redirect("playlist_tool:spotify_login")
    
    profile_data = response.json()
    spotify_profile, created = SpotifyProfile.objects.update_or_create(
        spotify_id=profile_data["id"],
        defaults={
            "display_name": profile_data.get("display_name", "Anonymous"),
            "image_url": profile_data["images"][0]["url"] if profile_data.get("images") else None,
            "followers": profile_data.get("followers", {}).get("total", 0),
        }
    )
        
    playlists_url = "https://api.spotify.com/v1/me/playlists"
    playlists_response = requests.get(playlists_url, headers=headers)
    
    if playlists_response.status_code != 200:
        logger.error(f"Failed to fetch Spotify playlists. Status code: {playlists_response.status_code}")
        return redirect("playlist_tool:spotify_login")
    
    playlists_data = playlists_response.json().get("items", [])
    logger.info(f"Fetched {len(playlists_data)} playlists for user {profile_data['id']}.")
    
    for playlist in playlists_data:
        if playlist is None or 'id' not in playlist:
            logger.warning("Skipping invalid playlist data.")
            continue
        Playlist.objects.update_or_create(
            spotify_profile=spotify_profile,
            playlist_id=playlist["id"],
            defaults={
                "name": playlist["name"],
                "image_url": playlist["images"][0]["url"] if playlist.get("images") else None,
                "spotify_url": playlist["external_urls"]["spotify"],
                "track_count": playlist["tracks"]["total"],
                "is_public": playlist["public"],
            }
        )

    playlists_data = Playlist.objects.filter(spotify_profile=spotify_profile).all()
    
    return render(request, "playlist_tool/profile.html", {
        "profile_data": profile_data,
        "playlists_data": playlists_data
    })

def fetch_tracks(request, playlist_id):
    access_token = request.session.get("access_token")
    if not access_token:
        logger.warning("No access token found in session. Redirecting to Spotify login.")
        return redirect("playlist_tool:spotify_login")
    
    playlist = get_object_or_404(Playlist, playlist_id=playlist_id)
    tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    current_track_ids = set()

    while tracks_url:
        response = requests.get(tracks_url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Failed to fetch tracks for playlist {playlist_id}. Status code: {response.status_code}")
            return JsonResponse({"error": "Failed to fetch tracks."}, status=400)
        
        tracks_data = response.json()
        for track in tracks_data["items"]:
            track_info = track["track"]
            current_track_ids.add(track_info["id"])
            
            artists = []
            for artist_data in track_info["artists"]:
                artist, created = Artist.objects.update_or_create(
                    name=artist_data["name"],
                    defaults={"artist_url": artist_data["external_urls"]["spotify"]}
                )
                artists.append(artist)
                
            track_obj, created = Track.objects.update_or_create(
                playlist=playlist,
                track_id=track_info["id"],
                defaults={
                    "name": track_info["name"],
                    "spotify_url": track_info["external_urls"]["spotify"],
                    "popularity": track_info["popularity"],
                }
            )
            
            track_obj.artists.set(artists)
            track_obj.save()
            
            audio_features_url = f"https://api.spotify.com/v1/audio-features/{track_info["id"]}"
            audio_response = requests.get(audio_features_url, headers=headers)
            
            if audio_response.status_code == 200:
                audio_features = audio_response.json()
                track_obj.danceability = audio_features.get("danceability")
                track_obj.energy = audio_features.get("energy")
                track_obj.tempo = audio_features.get("tempo")
                track_obj.valence = audio_features.get("valence")
                track_obj.instrumentalness = audio_features.get("instrumentalness")
                track_obj.save()
            else:
                logger.warning(f"Failed to fetch audio features for track {track_info['id']}. Assigning random values.")
                track_obj.danceability = random.uniform(0.0, 1.0)
                track_obj.energy = random.uniform(0.0, 1.0)
                track_obj.tempo = random.uniform(60.0, 200.0)
                track_obj.valence = random.uniform(0.0, 1.0)
                track_obj.instrumentalness = random.uniform(0.0, 1.0)
                track_obj.save()
        
        tracks_url = tracks_data["next"]
        
    existing_tracks = set(Track.objects.filter(playlist=playlist).values_list('track_id', flat=True))
    tracks_to_delete = existing_tracks - current_track_ids
    if tracks_to_delete:
        logger.info(f"Removing {len(tracks_to_delete)} tracks no longer in the playlist.")
        Track.objects.filter(playlist=playlist, track_id__in=tracks_to_delete).delete()
    
    playlist.analyzed = True
    playlist.save()
    
    return redirect("playlist_tool:view_statistics", playlist_id=playlist.playlist_id)

def view_statistics(request, playlist_id):
    playlist = get_object_or_404(Playlist, playlist_id=playlist_id)
    tracks = playlist.tracks.all()
    paginator = Paginator(tracks, 50)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    
    return render(request, "playlist_tool/statistics.html", {
        "playlist": playlist, 
        "page_obj": page_obj
    })

def fetch_top_tracks(request):
    access_token = request.session.get("access_token")
    if not access_token:
        logger.warning("No access token found in session. Redirecting to Spotify login.")
        return redirect("playlist_tool:spotify_login")
    
    time_range = request.GET.get("time_range", "short_term")
    limit = request.GET.get("limit", 50)
    
    top_tracks_url = f"https://api.spotify.com/v1/me/top/tracks"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "time_range": time_range,
        "limit": limit,
    }

    response = requests.get(top_tracks_url, headers=headers, params=params)
    
    if response.status_code == 200:
        return JsonResponse(response.json())
    elif response.status_code == 401:
        logger.warning("Access token expired or invalid. Redirecting to Spotify login.")
        return redirect("playlist_tool:spotify_login")
    else:
        logger.error(f"Failed to fetch top tracks. Status code: {response.status_code}, Response: {response.text}")
        return JsonResponse({"error": "Failed to fetch top tracks."}, status=response.status_code)
    
def top_tracks(request):
    return render(request, "playlist_tool/top_tracks.html")

def fetch_top_artists(request):
    access_token = request.session.get("access_token")
    if not access_token:
        logger.warning("No access token found in session. Redirecting to Spotify login.")
        return redirect("playlist_tool:spotify_login")
    
    time_range = request.GET.get("time_range", "short_term")
    limit = request.GET.get("limit", 50)
    
    top_artists_url = f"https://api.spotify.com/v1/me/top/artists"
    headers = {"Authorization": f"Bearer {access_token}"}
    params = {
        "time_range": time_range,
        "limit": limit,
    }
    
    response = requests.get(top_artists_url, headers=headers, params=params)
    
    if response.status_code == 200:
        return JsonResponse(response.json())
    elif response.status_code == 401:
        logger.warning("Access token expired or invalid. Redirecting to Spotify login.")
        return redirect("playlist_tool:spotify_login")
    else:
        logger.error(f"Failed to fetch top artists. Status code: {response.status_code}, Response: {response.text}")
        return JsonResponse({"error": "Failed to fetch top artists."}, status=response.status_code)
    
def top_artists(request):
    return render(request, "playlist_tool/top_artists.html")

def visualize_data(request, playlist_id):
    playlist = get_object_or_404(Playlist, playlist_id=playlist_id)
    tracks = playlist.tracks.all()
    
    track_names = [track.name for track in tracks]
    artists = [", ".join([artist.name for artist in track.artists.all()]) for track in tracks]  
    popularity = [track.popularity for track in tracks]
    danceability = [track.danceability for track in tracks]
    energy = [track.energy for track in tracks]
    tempo = [track.tempo for track in tracks]
    valence = [track.valence for track in tracks]
    
    data = {
        "track_names": track_names,
        "artists": artists,
        "popularity": popularity,
        "danceability": danceability,
        "energy": energy,
        "tempo": tempo,
        "valence": valence,
    }
    
    return render(request, "playlist_tool/visualize_data.html", {"data": data, "playlist": playlist,})