from spotipy import Spotify

from src.spotify.model import Player, Artist, Track, Playlist, Album, CurrentUser


class Root:
    def __init__(self, spotify: Spotify):
        self._spotify = spotify

    def player(self):
        return Player(self._spotify)

    def current_user(self):
        return CurrentUser(self._spotify)

    def track(self, id: str):
        return Track.from_id(self._spotify, id)

    def artist(self, id: str):
        return Artist.from_id(self._spotify, id)

    def playlist(self, id: str):
        return Playlist.from_id(self._spotify, id)

    def album(self, id: str):
        return Album.from_id(self._spotify, id)
