from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_login, name='home_login'),
    path('get-auth', views.AuthURL.as_view(), name='authorization'),
    path('redirect', views.spotify_callback, name='spotify_callback'),
    path('is-authenticated', views.IsAuthenticated.as_view(), name='is_auth'),
    path('user', views.CurrentUser.as_view(), name='current_user'),
    path('artist/<str:query>/', views.RelatedArtists.as_view(), name='related_artists'),
    path('album/<str:artist_id>/', views.GetAlbums.as_view(), name='get_albums')
]