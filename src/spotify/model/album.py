from src.spotify.track import artists_list
from src.spotify.model.resource import SpotifyResource


class Album(SpotifyResource):
    @staticmethod
    def from_id(spotify, id):
        return Album(spotify, spotify.album(id))

    def __init__(self, spotify, data: dict):
        super().__init__(spotify, lambda: spotify.album(self.id), data)

    @property
    def artists(self):
        return artists_list(self._data.get("artists"), self._spotify)

    @property
    def release_date(self):
        return self._data.get("release_date")

    def play(self):
        self._spotify.start_playback(context_uri=self.uri, offset={"position": 0})

    @property
    def total_tracks(self):
        return self._data.get("total_tracks")

    @property
    def popularity(self):
        return self._data.get("popularity")

    def save(self):
        self._spotify.current_user_saved_albums_add([self.id])
