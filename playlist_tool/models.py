from django.db import models

class SpotifyProfile(models.Model):
    spotify_id = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=100)
    image_url = models.URLField(blank=True, null=True)
    followers = models.IntegerField(default=0)
    
    def __str__(self):
        return self.display_name
    
class Playlist(models.Model):
    spotify_profile = models.ForeignKey(SpotifyProfile, on_delete=models.CASCADE, related_name="playlists")
    playlist_id = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    image_url = models.URLField(blank=True, null=True)
    track_count = models.IntegerField(default=0)
    is_public = models.BooleanField(default=True)
    analyzed = models.BooleanField(default=False)
    
    class Meta:
        ordering = ["name"]
    
    def __str__(self) -> str:
        return self.name
    

class Track(models.Model):
    playlist = models.ForeignKey(Playlist, on_delete=models.CASCADE, related_name="tracks")
    track_id = models.CharField(max_length=100)
    name = models.CharField(max_length=255)
    artist = models.CharField(max_length=255)
    danceability = models.FloatField(null=True, blank=True)
    energy = models.FloatField(null=True, blank=True)
    instrumentalness = models.FloatField(null=True, blank=True)
    tempo = models.FloatField(null=True, blank=True)
    valence = models.FloatField(null=True, blank=True)
    
    class Meta:
        ordering = ["name"]
        unique_together = ("playlist", "track_id")
    
    def __str__(self) -> str:
        return f"{self.name} by {self.artist}"
