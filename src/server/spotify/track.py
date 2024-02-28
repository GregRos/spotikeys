from typing import List

from spotipy import Spotify

from src.server.spotify import SpotifyResource
from src.server.spotify import Artist
from src.server.spotify import Album
from src.server.spotify.utils import not_none


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
        return Album(self._spotify, self.get("album"))

    @property
    def tracks(self):
        return [
            Track(self._spotify, track_data) for track_data in self._data.get("tracks")
        ]

    @property
    def artists(self) -> List[Artist]:
        return [
            Artist(self._spotify, artist_data)
            for artist_data in self._data.get("artists")
        ]

    @property
    def duration(self) -> float:
        return float(self.get("duration_ms")) / 1000

    def save(self):
        self._spotify.current_user_saved_tracks_add([self.id])

    @property
    def _artists_string(self):
        return ", ".join([artist.name for artist in self.artists])

    def __str__(self):
        return f"{self.__class__.name}({self._artists_string} - {self.name})"
