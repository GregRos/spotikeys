from spotipy import Spotify

from src.server.spotify.playlist import Playlist
from src.server.spotify.resource import SpotifyResource


class CurrentUser(SpotifyResource):
    def __init__(self, spotify: Spotify):
        def reload():
            return spotify.current_user()

        super().__init__(spotify, reload, reload())

    @property
    def playlists(self):
        from src.server.spotify.playlists import Playlists

        def reload():
            return self._spotify.current_user_playlists().get("items")

        return Playlists(
            self._spotify, self, [Playlist(self._spotify, p) for p in reload()]
        )

    @property
    def display_name(self):
        return self._data.get("display_name")

    @property
    def email(self):
        return self._data.get("email")

    @property
    def external_urls(self):
        return self._data.get("external_urls")

    @property
    def followers(self):
        return self._data.get("followers")

    @property
    def images(self):
        return self._data.get("images")

    @property
    def country(self):
        return self._data.get("country")

    @property
    def product(self):
        return self._data.get("product")

    def __str__(self):
        return self.display_name

    def __repr__(self):
        return f"SpotifyCurrentUser({self.display_name})"

    def __eq__(self, other):
        if isinstance(other, CurrentUser):
            return self.id == other.id
        return False

    def __hash__(self):
        return hash(self.id)
