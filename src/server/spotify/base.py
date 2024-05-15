from datetime import datetime
from time import sleep
from typing import Callable

from benedict import benedict
from spotipy import Spotify

from src.server.spotify.asyncify import asyncify

type Reload = Callable[[], dict]


class SpotifyBacked:
    _spotify: Spotify
    _retrieved: datetime

    def asyncily[R](self, func: Callable[[Spotify], R]):
        return asyncify(func)(self._spotify)

    def __init__(self, spotify: Spotify):
        self._spotify = spotify
        self._retrieved = datetime.now()


class SpotifyBase(SpotifyBacked):
    _data: benedict
    _spotify: Spotify
    _retrieved: datetime

    is_dirty: bool = False

    def __init__(
        self, spotify: Spotify, reload: Callable[[], dict | None], data: dict | None
    ):
        super().__init__(spotify)
        self._reload = reload
        self._data = benedict(data)

    def get(self, *keys):
        return self._data[keys]

    def set(self, key, value):
        if not key in self._data:
            raise ValueError(f"Key {key} not found!")
        self._data[key] = value

    def _verify_data(self, data: dict | None) -> dict:
        if not data:
            raise ValueError(f"Resource {self.__class__.__name__} not found!")
        return data

    def reload(self):
        sleep(0.4)
        result = self._reload()

        self._data = benedict(self._verify_data(result))

        self._retrieved = datetime.now()
        self.is_dirty = False
