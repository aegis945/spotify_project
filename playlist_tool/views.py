from django.shortcuts import redirect, render
from django.http import JsonResponse
from django.conf import settings
from django.middleware.csrf import get_token
from django.utils.http import urlencode

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
        "scope": "user-read-private user-read-email playlist-read-private",
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
