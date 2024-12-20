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
    path("fetch_top_tracks/", views.fetch_top_tracks, name="fetch_top_tracks"),
    path("top-tracks/", views.top_tracks, name="top_tracks"),
    path("fetch_top_artists/", views.fetch_top_artists, name="fetch_top_artists"),
    path("top-artists/", views.top_artists, name="top_artists"),
    path('visualize_data/<playlist_id>/', views.visualize_data, name='visualize_data'),
]
