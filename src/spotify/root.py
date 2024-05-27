from logging import getLogger
import time
from typing import TypedDict
from spotipy import Spotify, SpotifyOAuth


from src.spotify import Playback, Artist, Track, Playlist, Album, CurrentUser
from src.spotify.asyncify import asyncify
from src.spotify.device import Device
from src.spotify.utils import not_none


class SpotifyAuth(TypedDict):
    client_id: str
    client_secret: str
    redirect_uri: str


logger = getLogger("server")


class Root:

    def __init__(self, auth: SpotifyAuth):
        self._spotify = Spotify(
            auth_manager=SpotifyOAuth(
                **auth,
                scope=[
                    "user-library-read",
                    "user-read-playback-state",
                    "user-modify-playback-state",
                    "user-library-modify",
                    "user-follow-modify",
                    "user-read-currently-playing",
                    "user-read-recently-played",
                    # 'user-follow-read',
                    # 'user-top-read',
                    # 'user-read-playback-position',
                    "playlist-read-private",
                    # 'playlist-read-collaborative',
                    "playlist-modify-private",
                    "playlist-modify-public",
                    # 'app-remote-control'
                ],
            )
        )

        _orig_internal_call = self._spotify._internal_call

        def _internal_call(method, url, *args, **kwargs):
            start = time.time()
            try:
                result = _orig_internal_call(method, url, *args, **kwargs)
            except Exception as e:
                logger.error(f"{e}")
                raise
            else:
                logger.info(f"{method} {url}, got took {time.time() - start:.2f}s")
            return result

        self._spotify._internal_call = _internal_call  # type: ignore
        self._spotify._session.trust_env = False  # type: ignore
        self.me = CurrentUser(self._spotify)

    @asyncify
    def transfer_playback(self, device: Device | str, force=False):
        device = device.id if isinstance(device, Device) else device
        self._spotify.transfer_playback(device, force)

    @property
    @asyncify
    def playback(self):
        def reload():
            return self._spotify.current_playback()

        current = reload()
        if not current:
            return None
        return Playback(self._spotify, reload, current)

    @asyncify
    def track(self, id: str):
        return Track.from_id(self._spotify, id)

    @asyncify
    def artist(self, id: str):
        return Artist.from_id(self._spotify, id)

    @asyncify
    def get_devices(self):
        return [
            Device(**dev)
            for dev in not_none(self._spotify.devices()).get("devices", [])
        ]

    @asyncify
    def playlist(self, id: str):
        return Playlist.from_id(self._spotify, id)

    @asyncify
    def album(self, id: str):
        return Album.from_id(self._spotify, id)
