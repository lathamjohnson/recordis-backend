from django.shortcuts import render, redirect
from rest_framework.status import HTTP_200_OK
from .util import *
from pathlib import Path
from rest_framework.views import APIView, status
from rest_framework.response import Response
from requests import Request, post, get
from dotenv import load_dotenv
import os
import logging

def home_login(request):
    print("Redirect: ", os.getenv("REDIRECT_URI"))
    print("Client: ", os.getenv("CLIENT_ID") )
    return render(request, 'recordis_app/home_login.html')

class AuthURL(APIView):
    load_dotenv(dotenv_path=Path('.')/'.env')
    def get(self, request, format=None):
        scope = 'user-read-email user-read-private user-library-modify'
        url = Request('GET', 'https://accounts.spotify.com/authorize', params={
            'scope': scope,
            'response_type': 'code',
            'redirect_uri': os.getenv("REDIRECT_URI"),
            'client_id': os.getenv("CLIENT_ID"),
        }).prepare().url
        return Response({'url': url}, status=status.HTTP_200_OK)

class IsAuthenticated(APIView):
    def get(self, request, format=None):
        authenticated = is_authenticated(self.request.session.session_key)
        return Response({'status': authenticated}, status=status.HTTP_200_OK)


def spotify_callback(request, format=None):
    code = request.GET.get('code')
    error = request.GET.get('error')

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': os.getenv("REDIRECT_URI"),
        'client_id': os.getenv("CLIENT_ID"),
        'client_secret': os.getenv("CLIENT_SECRET"),
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    refresh_token = response.get('refresh_token')
    expires_in = response.get('expires_in')
    error = response.get('error')

    if not request.session.exists(request.session.session_key):
        request.session.create()
    update_or_create__user_tokens(request.session.session_key, access_token, token_type, expires_in, refresh_token)
    update_or_create__user(request.session.session_key)
    return redirect('http://localhost:3000/home')

class RelatedArtists(APIView):
    def get(self, request, query, format=None):
        user = SpotifyToken.objects.get(token_type='Bearer')
        output = []
        logging.debug(query)
        for q in query.rsplit(','):
            id = call_spotify_api(user, f'/search?q={q}&type=artist')['artists']['items'][0]["id"]
            artists = call_spotify_api(user, f'/artists/{id}/related-artists')
            for artist in artists["artists"]:
                if not artist["id"] in output:
                    output.append(artist["id"])
        return Response({'Artists': output}, status=status.HTTP_200_OK)

class CurrentUser(APIView):
    def get(self, request, format=None):
        user = SpotifyToken.objects.get(token_type='Bearer')
        response = call_spotify_api(user, '/me/')
        output = {
            'display_name' : response['display_name'],
            'email': response['email'],
            'id': response['id'],
        }
        return Response({'User': output}, status=status.HTTP_200_OK)


class GetAlbums(APIView):
    load_dotenv(dotenv_path=Path('.')/'.env')
    def get(self, request, artist_id):
        output = []
        token = SpotifyToken.objects.get(token_type='Bearer')
        response = call_spotify_api(token, f'/artists/{artist_id}/albums')
        for album in response["items"]:
            output.append({
                'name': album["name"],
                'artist': album["artists"][0]["name"], 
                'image': album["images"][0]["url"],
                'open_url': album["external_urls"]["spotify"]
                })
        return Response({'Results': output}, status=status.HTTP_200_OK)


# Create your views here.
