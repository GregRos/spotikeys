from dataclasses import dataclass, field
import re
from tkinter.ttk import Progressbar
from typing import Literal

import benedict
from spotipy import Spotify


from src.now_playing import MediaStatus
from src.server.spotify.asyncify import asyncify
from src.server.spotify.base import SpotifyBase
from src.server.spotify.track import Track

Repeat = Literal["track", "context", "off", None, False]
allowable_actions = (
    "interrupting_playback",
    "pausing",
    "resuming",
    "seeking",
    "skipping_next",
    "skipping_prev",
    "toggling_repeat_context",
    "toggling_repeat_track",
    "toggling_shuffle",
    "toggling_volume",
)


class NothingPlayingError(Exception):
    def __init__(self):
        super().__init__("No playback info!")


class Playback(SpotifyBase):

    def allows(self, action: str):
        disallows = self.get("actions").get("disallows").get(action)
        return not disallows

    def must_allow(self, action: str):
        if not self._data:
            raise NothingPlayingError()

        return action

    @property
    def saved(self):
        return self.get("is_saved")

    @property
    def track(self):
        return Track(self._spotify, self.get("item"))

    @property
    def is_playing(self) -> bool:
        return self.get("is_playing")

    @property
    def progress(self) -> float:
        return self.get("progress_ms") / 1000

    def get_status(self) -> MediaStatus:
        if self.is_dirty:
            self.reload()
        return MediaStatus(
            title=self.track.name,
            artist=self.track.artists[0].name,
            album=self.track.album.name,
            duration=self.track.duration,
            is_playing=self.is_playing,
            position=self.progress,
        )

    async def set_progress(self, progress: float):
        progress = int(max(0.0, min(progress, self.track.duration)) * 1000)
        self._spotify.seek_track(progress)
        self._data["progress_ms"] = int(progress)

    @asyncify
    def next_track(self):
        self._spotify.next_track()
        self.is_dirty = True

    @asyncify
    def prev_track(self):
        self._spotify.previous_track()
        self.is_dirty = True

    @property
    def volume(self) -> int:
        return self._data["device"]["volume_percent"]

    @asyncify
    def set_volume(self, volume: int):
        volume = max(0, min(volume, 100))
        self._spotify.volume(volume)
        self._data["device"]["volume_percent"] = volume

    @asyncify
    def play(self):
        self._spotify.start_playback()
        self.set("is_playing", True)

    @asyncify
    def pause(self):
        self._spotify.pause_playback()
        self.set("is_playing", False)

    @property
    def shuffle(self) -> bool:
        return self.get("shuffle_state")

    @shuffle.setter
    def shuffle(self, shuffle=False):
        self._spotify.shuffle(shuffle)
        self.set("shuffle_state", shuffle)

    @property
    def repeat(self) -> Literal["track", "context", False]:
        match self.get("repeat_state"):
            case "off":
                return False
            case repeat:
                return repeat

    @asyncify
    def set_repeat(self, repeat: Repeat):
        normalized = repeat if repeat else "off"
        self._spotify.repeat(normalized)
        self.set("repeat_state", normalized)
