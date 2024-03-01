from spotipy import Spotify

from src.server.spotify.artist import Artist
from src.server.spotify.resource import SpotifyResource


class Album(SpotifyResource):
    @staticmethod
    def from_id(spotify: Spotify, id: str):
        data = spotify.album(id)
        if not data:
            raise ValueError(f"Album with id {id} not found!")
        return Album(spotify, data)

    def __init__(self, spotify, data: dict):
        super().__init__(spotify, lambda: spotify.album(self.id), data)

    @property
    def artists(self):
        return [Artist(self._spotify, artist) for artist in self._data.get("artists")]

    @property
    def release_date(self):
        return self._data.get("release_date")

    def play(self):
        self._spotify.start_playback(context_uri=self.uri, offset={"position": 0})

    @property
    def total_tracks(self):
        return self._data.get("total_tracks")

    def unsave(self):
        self._spotify.current_user_saved_albums_delete([self.id])

    @property
    def popularity(self):
        return self._data.get("popularity")

    def save(self):
        self._spotify.current_user_saved_albums_add([self.id])
