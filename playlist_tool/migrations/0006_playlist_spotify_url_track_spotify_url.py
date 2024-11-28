# Generated by Django 5.1.2 on 2024-11-28 12:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playlist_tool', '0005_alter_playlist_options_alter_track_options'),
    ]

    operations = [
        migrations.AddField(
            model_name='playlist',
            name='spotify_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
        migrations.AddField(
            model_name='track',
            name='spotify_url',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]