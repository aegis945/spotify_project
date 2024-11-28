from django.shortcuts import get_object_or_404, redirect, render
from django.http import JsonResponse
from django.conf import settings
from django.middleware.csrf import get_token
from django.utils.http import urlencode
from .models import SpotifyProfile, Playlist, Track

import base64
import requests

def index(request):
    access_token = request.session.get("access_token")
    return render(request, "playlist_tool/index.html", {"access_token": access_token})

def spotify_login(request):
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
    try:
        code = request.GET.get("code")
        error = request.GET.get("error")
        state = request.GET.get("state")
    except KeyError:
        return JsonResponse({"error": "Missing parameters."}, status=400)
    
    if error:
        return JsonResponse({"error": error}, status=400)
    
    session_csrf_token = request.session.get("spotify_csrf_token")
    
    if not session_csrf_token:
        return JsonResponse({"error": "CSRF token not found in the session."}, status=400)
    
    if state != session_csrf_token:
        return JsonResponse({"error": "CSRF token mismatch."}, status=400)
    
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
    
    response = requests.post(token_url, data=form, headers=headers)
    
    if response.status_code == 200:
        tokens = response.json()
        access_token = tokens.get("access_token")
        refresh_token = tokens.get("refresh_token")
        expires_in = tokens.get("expires_in")

        request.session["access_token"] = access_token
        request.session["refresh_token"] = refresh_token
        request.session["expires_in"] = expires_in
        
        return redirect("playlist_tool:index")
    else:
        return JsonResponse(response.json(), status=response.status_code)
    
def spotify_logout(request):
    request.session.flush()
    return redirect("playlist_tool:index")

def profile(request):
    access_token = request.session.get("access_token")
    if not access_token:
        return redirect("playlist_tool:spotify_login")
    
    profile_url = "https://api.spotify.com/v1/me"
    headers = {"Authorization": f"Bearer {access_token}"}
    response = requests.get(profile_url, headers=headers)
    
    if response.status_code != 200:
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
        return redirect("playlist_tool:spotify_login")
    
    playlists_data = playlists_response.json().get("items", [])
        
    for playlist in playlists_data:
        if playlist is None or 'id' not in playlist:
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
        return redirect("playlist_tool:spotify_login")
    
    playlist = get_object_or_404(Playlist, playlist_id=playlist_id)
    tracks_url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {"Authorization": f"Bearer {access_token}"}
    
    while tracks_url:
        response = requests.get(tracks_url, headers=headers)
        if response.status_code != 200:
            return JsonResponse({"error": "Failed to fetch tracks."}, status=400)
        
        tracks_data = response.json()
        for track in tracks_data["items"]:
            track_info = track["track"]
            track_obj, created = Track.objects.update_or_create(
                playlist=playlist,
                track_id=track_info["id"],
                defaults={
                    "name": track_info["name"],
                    "artist": ", ".join(artist["name"] for artist in track_info["artists"]),
                    "spotify_url": track_info["external_urls"]["spotify"],
                }
            )
            
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
        
        tracks_url = tracks_data["next"]
        
    playlist.analyzed = True
    playlist.save()
    
    return redirect("playlist_tool:profile")

def view_statistics(request, playlist_id):
    playlist = get_object_or_404(Playlist, playlist_id=playlist_id)
    tracks = playlist.tracks.all()
    return render(request, "playlist_tool/statistics.html", {"playlist": playlist, "tracks": tracks})

def fetch_top_tracks(request):
    access_token = request.session.get("access_token")
    if not access_token:
        return redirect("playlist_tool:spotify_login")
    
    time_range = request.GET.get("time_range", "medium_term")
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
    else:
        return JsonResponse(response.json(), status=response.status_code)
    
def top_tracks(request):
    return render(request, "playlist_tool/top_tracks.html")