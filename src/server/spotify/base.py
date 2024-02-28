from ast import Match
from datetime import datetime
from time import sleep
from typing import Callable

from benedict import BeneDict as benedict
from spotipy import Spotify

type Reload = Callable[[], dict]


class SpotifyBase:
    _data: benedict
    _spotify: Spotify
    _retrieved: datetime

    def __init__(
        self, spotify: Spotify, reload: Callable[[], dict | None], data: dict | None
    ):
        self._reload = reload
        self._spotify = spotify
        self._data = benedict(data)
        self._retrieved = datetime.now()

    def get(self, key):
        return self._data[key]

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
