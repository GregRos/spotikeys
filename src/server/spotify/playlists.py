from typing import List
from src.server.spotify.base import SpotifyBacked, SpotifyBase
from src.server.spotify.current_user import CurrentUser
from src.server.spotify.playlist import Playlist
from src.server.spotify.resource import SpotifyResource
from spotipy import Spotify


class Playlists(SpotifyBacked):

    def __init__(
        self, spotify: Spotify, current_user: CurrentUser, playlists: List[Playlist]
    ):
        super().__init__(spotify)
        self._current_user = current_user
        self._playlists = playlists

    def add(self, name: str, public=True, description: str = ""):
        data = self._spotify.user_playlist_create(
            self._current_user.id, name, public=public, description=description
        )
        if data is None:
            raise ValueError("Failed to create playlist!")
        return Playlist(self._spotify, data)

    def __iter__(self):
        return iter(self._playlists)

    def __len__(self):
        return len(self._playlists)
