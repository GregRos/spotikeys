"""
A spotify track
"""

from spotipy import Spotify

from src.spotify.model.artist import Artist


def artists_list(artists: list, spotify: Spotify):
    return [Artist(spotify, artist) for artist in artists]


