import benedict
from spotipy import Spotify

from src.remote.model.base import SpotifyBase
from src.remote.model.track import Track


class Player(SpotifyBase):
    def __init__(self, spotify: Spotify):
        def current_playback():
            return spotify.current_playback()

        super().__init__(spotify, current_playback, current_playback())

    @property
    def track(self):
        return Track(self._spotify, self._data.get("item"))

    @property
    def is_playing(self) -> bool:
        return self._data.get("is_playing")

    @property
    def progress(self) -> int:
        return self._data.get("progress_ms") / 1000

    @progress.setter
    def progress(self, progress: int):
        self._spotify.seek_track(progress * 1000)

    def next_track(self):
        self._spotify.next_track()

    def prev_track(self):
        self._spotify.previous_track()

    @property
    def shuffle(self) -> bool:
        return self._data.get("shuffle_state")
