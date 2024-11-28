from django.contrib import admin
from .models import Artist, SpotifyProfile, Playlist, Track

admin.site.register(Artist)
admin.site.register(SpotifyProfile)
admin.site.register(Playlist)
admin.site.register(Track)
