from django.urls import path
from . import views

urlpatterns = [
    path("", views.index2, name="index2"),
    path("spotify-auth/", views.spotify_auth, name="spotify_auth"),
    path("spotify_redirect/", views.spotify_redirect, name="spotify_redirect"),
    path('refresh_token/', views.refresh_token, name='refresh_token'),
    path("fetch_data/", views.fetch_data, name="fetch_data")
]