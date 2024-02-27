from spotipy import Spotify, SpotifyOAuth

from src.server.spotify import Playback, Artist, Track, Playlist, Album, CurrentUser


class Root:
    def __init__(self, client_id: str, client_secret: str, redirect_uri: str):
        auth_manager = SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri=redirect_uri,
            scope=",".join(scopes),
        )
        self._spotify = Spotify(auth_manager=auth_manager)
        self._spotify._session.trust_env = False

    @property
    def playback(self):
        def reload():
            return self._spotify.current_playback()
        current = reload()
        if not current:
            return None
        return Playback(self._spotify, reload, current)

    @property
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
