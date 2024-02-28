from spotipy import Spotify

from src.server.spotify.resource import SpotifyResource


class Artist(SpotifyResource):
    @staticmethod
    def from_id(spotify: Spotify, id):
        return Artist(spotify, spotify.artist(id))

    def __init__(self, spotify, data: dict| None):
        super().__init__(spotify, lambda: spotify.artist(self.id), data)

    @property
    def genres(self):
        return self._data.get("genres")

    @property
    def popularity(self):
        return self._data.get("popularity")

    def follow(self):
        self._spotify.user_follow_artists(self.id)

    def play(self):
        self._spotify.start_playback(context_uri=self.uri)

    def save(self):
        self._spotify.user_follow_artists([self.id])