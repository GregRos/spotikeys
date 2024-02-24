from typing import Literal

import benedict
from spotipy import Spotify

from src.spotify.base import SpotifyBase
from src.spotify.track import Track


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
        progress = max(0, min(progress, self.track.duration))
        self._spotify.seek_track(progress * 1000)

    def next_track(self):
        self._spotify.next_track()

    def prev_track(self):
        self._spotify.previous_track()

    @property
    def shuffle(self) -> bool:
        return self._data.get("shuffle_state")

    @shuffle.setter
    def shuffle(self, shuffle: bool):
        self._spotify.shuffle(shuffle)

    @property
    def repeat(self):
        return self._data.get("repeat_state")

    @repeat.setter
    def repeat(self, repeat: Literal["track", "context", "off", None, False]):
        normalized = repeat if repeat else "off"
        self._spotify.repeat(normalized)
