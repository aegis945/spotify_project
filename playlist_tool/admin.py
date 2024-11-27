from django.contrib import admin
from .models import SpotifyProfile, Playlist, Track

admin.site.register(SpotifyProfile)
admin.site.register(Playlist)
admin.site.register(Track)
