from django.urls import path
from . import views

app_name = "playlist_tool"

urlpatterns = [
    path("", views.index, name="index"),
    path("spotify/login", views.spotify_login, name="spotify_login"),
    path("spotify/logout", views.spotify_logout, name="spotify_logout"),
    path("callback", views.spotify_callback, name="spotify_callback"),
    path("profile/", views.profile, name="profile"),
    path("fetch_tracks/<str:playlist_id>/", views.fetch_tracks, name="fetch_tracks"),
    path("view_statistics/<str:playlist_id>/", views.view_statistics, name="view_statistics"),
    path('fetch-top-tracks/', views.fetch_top_tracks, name='fetch_top_tracks'),
    path("top-tracks/", views.top_tracks, name="top_tracks"),
]
