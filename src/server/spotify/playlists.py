from logging import getLogger
from typing import Callable, List
from src.server.spotify.asyncify import asyncify
from src.server.spotify.base import SpotifyBacked, SpotifyBase
from src.server.spotify.current_user import CurrentUser
from src.server.spotify.playlist import Playlist
from src.server.spotify.resource import SpotifyResource
from spotipy import Spotify

logger = getLogger("server")


class Playlists(SpotifyBacked):

    def __init__(self, spotify: Spotify, current_user: CurrentUser):
        super().__init__(spotify)
        self._current_user = current_user

    @asyncify
    def add(self, name: str, public=True, description: str = ""):
        data = self._spotify.user_playlist_create(
            self._current_user.id, name, public=public, description=description
        )
        if data is None:
            raise ValueError("Failed to create playlist!")
        playlist = Playlist(self._spotify, data)

        logger.info(f"Created playlist {playlist.name}")
        return playlist

    async def items(self):
        playlists_result = await self.asyncily(
            lambda spot: spot.current_user_playlists().get("items")
        )
        playlists = [Playlist(self._spotify, p) for p in playlists_result]
        logger.info(f"Loaded {len(playlists)} playlists")
        return playlists
