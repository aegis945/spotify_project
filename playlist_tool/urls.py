from django.urls import path
from . import views

app_name = "playlist_tool"

urlpatterns = [
    path("", views.index, name="index"),
    path("spotify/login", views.spotify_login, name="spotify_login"),
    path("spotify/logout", views.spotify_logout, name="spotify_logout"),
    path("callback", views.spotify_callback, name="spotify_callback"),
    path("profile/", views.profile, name="profile"),
]
