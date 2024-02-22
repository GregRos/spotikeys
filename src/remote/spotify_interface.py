import json
import time
from os import path

import spotipy
from spotipy import SpotifyOAuth, Spotify
from benedict import benedict
from typing import Callable, Any, Literal, TypeAlias

from src.remote.operators import (
    get_artist,
    get_album,
    is_different_artists,
    is_different_albums,
    is_different_tracks,
    get_track,
)

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


MusicType: TypeAlias = Literal["album", "artist", "all", "track"]


def pick_dif_function(what: MusicType):
    match what:
        case "album":
            return is_different_albums
        case "artist":
            return is_different_artists
        case "track":
            return is_different_tracks
        case "all":
            return lambda x, y: False
        case _:
            raise Exception(f"Expected {what} to be a valid start type")


def is_muted(obj: benedict):
    if obj.get("device.volume_percent") != 0:
        return False
    if not path.isfile("./vol.txt"):
        return False
    return True


default_max = 30

backtrack_before = 10 * 1000


class SpotifyInterface:
    _spotify: Spotify

    def __init__(self):
        start = time.time()
        self._spotify = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id="b996e2c82b574509bec24fbd11eda035",
                client_secret="2370df9b5a7840a183f44bbd795483fa",
                scope=",".join(scopes),
                redirect_uri="http://localhost:12000",
            )
        )
        self._spotify._session.trust_env = False
        print(json.dumps(self.hist()))

    def _get_current_track(self):
        return benedict(self._spotify.currently_playing())

    def _get_current(self):
        return benedict(self._spotify.current_playback())

    def seek_time(self, mod: int) -> None:
        current = self._get_current()
        progress = current.get("progress_ms", None)
        if progress is None:
            return
        new_progress = max(0, progress + mod)
        self._spotify.seek_track(new_progress)

    def _skim_while(self, op: Callable[[], Any], max_ops=default_max):
        prev_ts = 0
        for i in range(max_ops):
            op()
            time.sleep(0.25)
            playback = self._get_current()
            cur_ts = playback.get("timestamp")
            if prev_ts == cur_ts:
                time.sleep(0.25)
                playback = self._get_current()
            prev_ts = cur_ts
            yield [playback, i]
            if playback.get("actions.disallows.skipping_prev", False):
                return

    def hist(self):
        return self._spotify.current_user_recently_played()

    def restart_track(self):
        self._spotify.seek_track(0)

    def prev_track(self):
        self._spotify.previous_track()

    def next_track(self, count=1):
        for i in range(0, count):
            self._spotify.next_track()

    def toggle_pause(self):
        current = self._get_current()
        if current.get("is_playing"):
            self._spotify.pause_playback()
        else:
            self._spotify.start_playback()

    def restart_thing(self):
        initial = self._get_current()
        old_repeat = initial.get("repeat_state")
        if old_repeat != "off":
            self._spotify.repeat("off")
        for [current, count] in self._skim_while(
            lambda: self._spotify.previous_track()
        ):
            pass
        if old_repeat != "off":
            self._spotify.repeat(old_repeat)

    def set_repeat(self, mode):
        self._spotify.repeat(mode)

    def rename_playlist(self, playlist: str, new_name: str, new_desc: str):
        self._spotify.playlist_change_details(
            playlist_id=playlist, name=new_name, description=new_desc
        )

    def start_playlist(self, playlist: str):
        pl = self._spotify.playlist(playlist_id=playlist)
        self._spotify.start_playback(context_uri=pl["uri"], offset={"position": 0})

    def skip_album(self):
        initial = self._get_current()
        old_repeat = initial.get("repeat_state")
        if old_repeat != "off":
            self._spotify.repeat("off")

        for [current, count] in self._skim_while(lambda: self._spotify.next_track()):
            if is_different_albums(initial, current):
                break

        if old_repeat != "off":
            self._spotify.repeat("off")

    def heart_track(self):
        current = self._get_current()
        track = get_track(current)
        self._spotify.current_user_saved_tracks_add([track])

    def heart_album(self):
        current = self._get_current()
        album = get_album(current)
        self._spotify.current_user_saved_albums_add([album])

    def follow_artist(self):
        current = self._get_current()
        artist = get_artist(current)
        self._spotify.user_follow_artists([artist])

    def dump_currently_playing(self):
        playing = self._get_current()
        print(json.dumps(playing))

    def clean_playlist(self, target_plid: str):
        my_playlist = self.find_automated_playlist()
        result = self._spotify.playlist_items(playlist_id=target_plid)
        all_uris = [track.get("track").get("id") for track in result.get("items")]
        self._spotify.playlist_remove_all_occurrences_of_items(
            playlist_id=my_playlist, items=all_uris
        )

    def find_automated_playlist(self):
        all_playlists = self._spotify.current_user_playlists()
        for playlist in all_playlists.get("items"):
            if "⚙️" in playlist.get("item.name"):
                return playlist

    def spin_song(self):
        playback = self._get_current()
        artist_name = playback.get("item.artists[0].name")
        track_name = playback.get("item.name")
        generated_for = f"⚙️ LIKE « {artist_name} - {track_name} »"
        my_playlist = self.find_automated_playlist()
        self.rename_playlist(my_playlist, generated_for, "Generated automatically.")
        uri = playback.get("item.uri")
        recs = benedict(self._spotify.recommendations(seed_tracks=[uri]))
        tracks = [track.get("id") for track in recs.get("tracks")]
        self.clean_playlist(my_playlist)
        self._spotify.playlist_add_items(my_playlist, tracks)
        time.sleep(1)
        self.start_playlist(my_playlist)

    def spin_album(self):
        playback = self._get_current()
        album_uri = playback.get("item.album.uri")
        self._spotify.start_playback(context_uri=album_uri, offset={"position": 0})

    def spin_artist(self):
        playback = self._get_current()
        artist_uri = playback.get("item.artists[0].uri")
        self._spotify.start_playback(context_uri=artist_uri)
