from spotipy import Spotify, SpotifyOAuth

from src.remote.spotify import Player, Artist, Track, Playlist, Album, CurrentUser


class Root:
    def __init__(self):
        auth_manager = SpotifyOAuth(
            client_id="b996e2c82b574509bec24fbd11eda035",
            client_secret="2370df9b5a7840a183f44bbd795483fa",
            scope=",".join(scopes),
            redirect_uri="http://localhost:12000",
        )
        self._spotify = Spotify(auth_manager)

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


scopes = [
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
    # 'app-remote-control'
]
