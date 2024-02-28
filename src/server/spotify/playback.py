import re
from typing import Literal

import benedict
from spotipy import Spotify

from src.server.spotify.base import SpotifyBase
from src.server.spotify.track import Track


class NothingPlayingError(Exception):
    def __init__(self):
        super().__init__("No playback info!")


class Playback(SpotifyBase):

    @property
    def track(self):
        return Track(self._spotify, self.get("item"))

    @property
    def is_playing(self) -> bool:
        return self.get("is_playing")

    @property
    def progress(self) -> float:
        return self.get("progress_ms") / 1000

    @progress.setter
    def progress(self, progress: float):
        progress = max(0.0, min(progress, self.track.duration))
        self._spotify.seek_track(int(progress * 1000))
        self.reload()

    def next_track(self):
        self._spotify.next_track()
        self.reload()

    def prev_track(self):
        self._spotify.previous_track()
        self.reload()

    @property
    def volume(self) -> int:
        return self._data["device"]["volume_percent"]

    @volume.setter
    def volume(self, volume: int):
        volume = max(0, min(volume, 100))
        self._spotify.volume(volume)
        self._data["device"]["volume_percent"] = volume

    def play(self):
        self._spotify.start_playback()
        self.set("is_playing", True)

    def pause(self):
        self._spotify.pause_playback()
        self.set("is_playing", False)

    @property
    def shuffle(self) -> bool:
        return self.get("shuffle_state")

    @shuffle.setter
    def shuffle(self, shuffle: bool):
        self._spotify.shuffle(shuffle)
        self.set("shuffle_state", shuffle)

    @property
    def repeat(self) -> Literal["track", "context", False]:
        match self.get("repeat_state"):
            case "off":
                return False
            case repeat:
                return repeat

    @repeat.setter
    def repeat(self, repeat: Literal["track", "context", "off", None, False]):
        normalized = repeat if repeat else "off"
        self._spotify.repeat(normalized)
        self.set("repeat_state", normalized)
