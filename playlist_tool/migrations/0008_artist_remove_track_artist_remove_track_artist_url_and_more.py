# Generated by Django 5.1.2 on 2024-11-28 14:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('playlist_tool', '0007_track_artist_url'),
    ]

    operations = [
        migrations.CreateModel(
            name='Artist',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('artist_url', models.URLField(blank=True, max_length=250, null=True)),
            ],
        ),
        migrations.RemoveField(
            model_name='track',
            name='artist',
        ),
        migrations.RemoveField(
            model_name='track',
            name='artist_url',
        ),
        migrations.AddField(
            model_name='track',
            name='artists',
            field=models.ManyToManyField(related_name='tracks', to='playlist_tool.artist'),
        ),
    ]