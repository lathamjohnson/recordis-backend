from django.db import models


class Album(models.Model):
    title = models.CharField(max_length=100)
    artist = models.CharField(max_length=100)
    year = models.PositiveIntegerField()
    cover_url = models.CharField(max_length=250)
    spotify_url = models.CharField(max_length=250)

    def __str__(self):
        return self.title

class SpotifyToken(models.Model):
    user = models.CharField(max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    refresh_token = models.CharField(max_length=250)
    access_token = models.CharField(max_length=250)
    expires_in = models.DateTimeField()
    token_type = models.CharField(max_length=50)

    def __str__(self):
        return self.user

class User(models.Model):
    username = models.CharField(max_length=150)
    password = models.CharField(max_length=50)
    token = models.ForeignKey(SpotifyToken, on_delete=models.CASCADE, related_name='local_user')
    favorites = models.ManyToManyField(Album)

    def __str__(self):
        return self.username

# Create your models here.
