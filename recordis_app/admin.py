from django.contrib import admin
from .models import User, Album, SpotifyToken

admin.site.register(User)
admin.site.register(Album)
admin.site.register(SpotifyToken)

# Register your models here.
