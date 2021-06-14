from datetime import timedelta
import logging
from requests.sessions import session
from .models import User, SpotifyToken, Album
from django.utils import timezone
from dotenv import load_dotenv
from pathlib import Path
from requests import post, put, get
import os

BASE_URL = 'https://api.spotify.com/v1'

def get_user_tokens(session_id):
    user_tokens = SpotifyToken.objects.filter(user=session_id)
    if user_tokens.exists():
        return user_tokens[0]
    else:
        return None

def update_or_create__user_tokens(session_id, access_token, token_type, expires_in, refresh_token):
    tokens = get_user_tokens(session_id)
    expires_in = timezone.now() + timedelta(seconds=expires_in)
    if tokens:
        tokens.access_token = access_token
        tokens.refresh_token = refresh_token
        tokens.token_type = token_type
        tokens.save(update_fields=['access_token', 'refresh_token', 'expires_in', 'token_type'])
    else:
        tokens = SpotifyToken(
            user=session_id, 
            access_token=access_token, 
            refresh_token=refresh_token, 
            token_type=token_type, 
            expires_in=expires_in 
            ).save() 


def is_authenticated(session_id):
    tokens = get_user_tokens(session_id)
    if tokens:
        expiry = tokens.expires_in
        if expiry <= timezone.now():
            refresh_token(session_id)
        return True    
    return False

def refresh_token(session_id):
    refresh_token = get_user_tokens(session_id).refresh_token
    load_dotenv(dotenv_path=Path('.')/'.env')

    response = post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': os.getenv("CLIENT_ID"),
        'client_secret': os.getenv("CLIENT_SECRET")
    }).json()

    access_token = response.get('access_token')
    token_type = response.get('token_type')
    expires_in = response.get('expires_in')
    refresh_token = response.get('refresh_token')

    update_or_create__user_tokens(session_id, access_token, token_type, expires_in, refresh_token)

def call_spotify_api(session_id, endpoint, post_=False, put_=False):
    tokens = get_user_tokens(session_id)
    header = {'Content-Type': 'application/json', 'Authorization': f"Bearer {tokens.access_token}"}
    if post_:
        post(BASE_URL + endpoint, headers=header)
    if put_:
        put(BASE_URL + endpoint, headers=header)
    response = get(BASE_URL + endpoint, {}, headers=header)
    try:
        return response.json()
    except: 
        return {'Error': 'Issue with request'}

def update_or_create__user(session_id):
    spotify_user = call_spotify_api(session_id, '/me')
    try:
        User.objects.filter(password=spotify_user['id']).update(
            token=SpotifyToken.objects.get(user=session_id)
        )
    except User.DoesNotExist:
        User(
            username=spotify_user['display_name'],
            password=spotify_user['id'],
            token=SpotifyToken.objects.get(user=session_id)
        ).save()

       

