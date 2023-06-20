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
    auth_url = f"https://accounts.spotify.com/authorize?client_id={settings.SPOTIFY_CLIENT_ID}&response_type=token&redirect_uri={redirect_uri}&scope={scopes}"
    return HttpResponseRedirect(auth_url)

def index(request):
    return HttpResponse("Hello, World!")


def index2(request):
    return render(request, "index.html")


def spotify_redirect(request):
    # Extract the access token from the URL
    url = request.build_absolute_uri()
    parsed = urlparse(url)
    params = parse_qs(parsed.fragment)
    access_token = params.get('access_token', [None])[0]

    # Save the access token to the session
    if access_token:
        request.session['access_token'] = access_token

    # Redirect to fetch_data view
    return redirect('fetch_data')

@csrf_exempt
def fetch_data(request):
    access_token = request.GET.get('access_token')

    headers = {
        'Authorization': f'Bearer {access_token}',
    }

    # Get the user's profile information
    user_profile_response = requests.get('https://api.spotify.com/v1/me', headers=headers)
    user_profile_data = user_profile_response.json()
    username = user_profile_data.get('display_name', 'Unknown user')
    

    # Define parameters for the requests
    params = {
        'limit': 50
    }

    # Fetch short term top artists
    params['time_range'] = 'short_term'
    short_term_top_artists_response = requests.get('https://api.spotify.com/v1/me/top/artists', headers=headers, params=params)

    # Fetch long term top artists
    params['time_range'] = 'long_term'
    long_term_top_artists_response = requests.get('https://api.spotify.com/v1/me/top/artists', headers=headers, params=params)

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
            "profile_picture": profile_picture,
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

