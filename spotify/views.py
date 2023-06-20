from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.conf import settings
from urllib.parse import quote
import requests
from django.views.decorators.csrf import csrf_exempt
from .helpers import mapping, map_personality_to_color
from django.shortcuts import redirect
from urllib.parse import urlparse, parse_qs



def spotify_auth(request):
    redirect_uri = quote('https://vibevalidator-066e2269d7e5.herokuapp.com/spotify_redirect')
    scopes = quote('user-top-read user-read-private user-read-email')
    auth_url = f"https://accounts.spotify.com/authorize?client_id={settings.SPOTIFY_CLIENT_ID}&response_type=code&redirect_uri={redirect_uri}&scope={scopes}"
    return HttpResponseRedirect(auth_url)


def index(request):
    return HttpResponse("Hello, World!")


def index2(request):
    return render(request, "index.html")


def spotify_redirect(request):
    code = request.GET.get('code')
    redirect_uri = 'https://vibevalidator-066e2269d7e5.herokuapp.com/spotify_redirect'
    token_response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'authorization_code',
        'code': code,
        'redirect_uri': redirect_uri,
        'client_id': settings.SPOTIFY_CLIENT_ID,
        'client_secret': settings.SPOTIFY_CLIENT_SECRET,
    })
    token_data = token_response.json()
    access_token = token_data['access_token']
    refresh_token = token_data['refresh_token']
    # Save these tokens in the session
    request.session['access_token'] = access_token
    request.session['refresh_token'] = refresh_token
    return redirect('fetch_data')


def refresh_token(request):
    # Retrieve the refresh token from the session
    refresh_token = request.session.get('refresh_token')
    token_response = requests.post('https://accounts.spotify.com/api/token', data={
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token,
        'client_id': settings.SPOTIFY_CLIENT_ID,
        'client_secret': settings.SPOTIFY_CLIENT_SECRET,
    })
    token_data = token_response.json()
    access_token = token_data['access_token']
    # Save the new access token in the session
    request.session['access_token'] = access_token
    return redirect('fetch_data')



@csrf_exempt
def fetch_data(request):
    access_token = request.session.get('access_token')

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    # Get the user's profile information
    user_profile_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    print(f"User profile status code: {user_profile_response.status_code}")
    print(f"User profile response text: {user_profile_response.text}")   
    user_profile_data = user_profile_response.json()
    username = user_profile_data.get('display_name', 'Unknown user')
    
    # Define parameters for the requests
    params = {
        'limit': 50
    }

    # Fetch short term top artists
    params['time_range'] = 'short_term'
    short_term_top_artists_response = requests.get('https://api.spotify.com/v1/me/top/artists', headers=headers, params=params)
    print(f"Short term top artists status code: {short_term_top_artists_response.status_code}")
    print(f"Short term top artists response text: {short_term_top_artists_response.text}")

    # Fetch long term top artists
    params['time_range'] = 'long_term'
    long_term_top_artists_response = requests.get('https://api.spotify.com/v1/me/top/artists', headers=headers, params=params)
    print(f"Long term top artists status code: {long_term_top_artists_response.status_code}")
    print(f"Long term top artists response text: {long_term_top_artists_response.text}")

    if short_term_top_artists_response.status_code == 200 and long_term_top_artists_response.status_code == 200 and user_profile_response.status_code == 200:
        short_term_top_artists_data = short_term_top_artists_response.json()
        long_term_top_artists_data = long_term_top_artists_response.json()

        # Extracting the names, genres and images
        short_term_top_genre = [(artist['genres']) for artist in short_term_top_artists_data['items']]
        short_term_top_photos = [(artist['images'][0]['url'] if artist['images'] else 'No artist image') for artist in short_term_top_artists_data['items']]
        your_personality = mapping(short_term_top_genre)
        your_color = map_personality_to_color(your_personality)
        long_term_top_genre = [(artist['genres']) for artist in long_term_top_artists_data['items']]
        long_term_top_photos = [(artist['images'][0]['url'] if artist['images'] else 'No artist image') for artist in long_term_top_artists_data['items']]
        your_longterm_personality = mapping(long_term_top_genre)
        your_longterm_color = map_personality_to_color(your_longterm_personality)

        data = {
            "username": username,
            # "profile_picture": profile_picture,
            "current_personality": your_personality,
            "short_term_top_photos": short_term_top_photos,
            "current_color" : your_color,
            "long_term_top_photos": long_term_top_photos,
            "longterm_personality": your_longterm_personality,
            "longterm_color": your_longterm_color
        }

        return render(request, "result.html", data)

    else:
        short_term_error = short_term_top_artists_response.json()
        long_term_error = long_term_top_artists_response.json()
        user_profile_error = user_profile_response.json()
        error_data = {
            "user_profile_data" : user_profile_data,
            "short_term_error": short_term_error,
            "long_term_error": long_term_error,
            "user_profile_error": user_profile_error,
        }
        print(error_data)  # or use logging module
        return HttpResponse("Error retrieving data from Spotify. Details: " + str(error_data))

