from datetime import datetime
from typing import Callable

from benedict import BeneDict as benedict
from spotipy import Spotify

type Reload = Callable[[], dict]


class SpotifyBase:
    _data: benedict
    _spotify: Spotify
    _reload: Reload
    _retrieved: datetime

    def __init__(self, spotify: Spotify, reload: Callable[[], dict], data: dict):
        self._reload = reload
        self._spotify = spotify
        self._data = benedict(data)
        self._retrieved = datetime.now()

    def reload(self):
        self._data = benedict(self._reload())
        self._retrieved = datetime.now()
