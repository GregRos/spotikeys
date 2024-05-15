from logging import getLogger
from typing import List, cast

from spotipy import Spotify

from src.server.spotify.resource import SpotifyResource
from src.server.spotify.artist import Artist
from src.server.spotify.album import Album
from src.server.spotify.asyncify import asyncify
from src.server.spotify.utils import not_none

logger = getLogger("server")


class Track(SpotifyResource):

    def __init__(self, spotify: Spotify, data: dict):
        super().__init__(spotify, lambda: spotify.track(self.id), data)

    @staticmethod
    def from_id(spotify: Spotify, id: str):
        return Track(spotify, not_none(spotify.track(id)))

    def play(self):
        self._spotify.start_playback(uris=[self.uri])

    @property
    def album(self):
        if not self._data.get("album"):
            return None
        return Album(self._spotify, cast(dict, self._data.get_dict("album")))

    @property
    def tracks(self):
        return [
            Track(self._spotify, track_data) for track_data in self._data.get("tracks")
        ]

    @asyncify
    def recommend(self):
        result = [
            Track(self._spotify, track_data)
            for track_data in not_none(
                self._spotify.recommendations(seed_tracks=[self.id])
            ).get("tracks")
        ]
        logger.info(f"Recommended {len(result)} tracks for {self.name}")
        return result

    @property
    def artists(self) -> List[Artist]:
        return [
            Artist(self._spotify, artist_data)
            for artist_data in self._data.get("artists")
        ]

    @property
    def duration(self) -> float:
        return float(self._data.get_int("duration_ms")) / 1000

    async def set_saved(self, saved: bool):
        if saved:
            await self.save()
        else:
            await self.unsave()

    async def save(self):
        if await self.is_saved:
            return False
        await self.asyncily(lambda spot: spot.current_user_saved_tracks_add([self.id]))
        return True

    @property
    @asyncify
    def is_saved(self):
        return not_none(self._spotify.current_user_saved_tracks_contains([self.id]))[0]

    async def unsave(self):
        if await self.is_saved:
            return False
        await self.asyncily(
            lambda spot: spot.current_user_saved_tracks_delete([self.id])
        )
        return True

    @property
    def artists_string(self):
        return ", ".join([artist.name for artist in self.artists])

    def __str__(self):
        return f"{self.__class__.name}({self.artists_string} - {self.name})"
