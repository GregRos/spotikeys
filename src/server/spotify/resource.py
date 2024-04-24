from typing import Callable

from spotipy import Spotify

from src.server.spotify.base import SpotifyBase


class SpotifyResource(SpotifyBase):
    def __init__(
        self, spotify: Spotify, reload: Callable[[], dict | None], data: dict | None
    ):
        super().__init__(spotify, reload, data)

    @property
    def name(self) -> str:
        return str(self._data.get("name") or self._data.get("display_name"))

    @property
    def id(self) -> str:
        return str(self._data.get("id"))

    @property
    def uri(self):
        return str(self._data.get("uri"))

    def __str__(self):
        return f"{self.__class__.name}({self.name})"

    def __repr__(self):
        return f"{self.__class__.name}({self.name})"
