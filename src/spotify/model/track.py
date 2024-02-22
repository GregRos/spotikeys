from typing import List

from spotipy import Spotify

from src.spotify.track import artists_list
from src.spotify.model.resource import SpotifyResource
from src.spotify.model.artist import Artist
from src.spotify.model.album import Album


class Track(SpotifyResource):

    @staticmethod
    def from_id(spotify: Spotify, id: str):
        return Track(spotify, spotify.track(id))

    def __init__(self, spotify: Spotify, data: dict):
        super().__init__(spotify, lambda: spotify.track(self.id), data)

    def play(self):
        self._spotify.start_playback(uris=[self.uri])

    @property
    def album(self):
        return Album(self._spotify, self._data.get("album"))

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
    def duration(self) -> int:
        return self._data.get("duration_ms") * 1000

    def save(self):
        self._spotify.current_user_saved_tracks_add([self.id])

    @property
    def popularity(self) -> int:
        return self._data.get("popularity")

    @property
    def _artists_string(self):
        return ", ".join([artist.name for artist in self.artists])

    def __str__(self):
        return f"{self.__class__.name}({self._artists_string} - {self.name})"
