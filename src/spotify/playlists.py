from logging import getLogger
from src.spotify.asyncify import asyncify
from src.spotify.base import SpotifyBacked
from src.spotify.current_user import CurrentUser
from src.spotify.playlist import Playlist
from spotipy import Spotify

from src.spotify.utils import not_none

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
            lambda spot: not_none(spot.current_user_playlists()).get("items")
        )
        playlists = [Playlist(self._spotify, p) for p in playlists_result]
        logger.info(f"Loaded {len(playlists)} playlists")
        return playlists
