from typing import List

from spotipy import Spotify

from src.spotify.model.track import Track
from src.spotify.model.resource import SpotifyResource
from src.spotify.model.artist import Artist
from benedict import BeneDict as benedict


class Playlist(SpotifyResource):
    @staticmethod
    def from_id(spotify: Spotify, id: str):
        return Playlist(spotify, spotify.playlist(id))

    def __init__(self, spotify: Spotify, data: dict):
        super().__init__(spotify, lambda: spotify.playlist(self.id), data)

    def play(self):
        self._spotify.start_playback(context_uri=self.uri)

    @property
    def name(self):
        return self._data.get("name")

    def follow(self):
        self._spotify.current_user_follow_playlist(self.id)

    def unfollow(self):
        self._spotify.current_user_unfollow_playlist(self.id)

    @SpotifyResource.name.setter
    def name(self, name):
        self._spotify.playlist_change_details(self.id, name=name)
        self._data["name"] = name

    @property
    def images(self) -> List[dict]:
        return self._data.get("images")

    def reload(self):
        self._data = benedict(self._spotify.playlist(self.id))

    def add_tracks(self, tracks: List[str]):
        self._spotify.playlist_add_items(self.id, tracks)
        self.reload()

    def remove_tracks(self, tracks: List[str]):
        self._spotify.playlist_remove_all_occurrences_of_items(self.id, tracks)
        self._data["tracks"]["items"] = [
            track
            for track in self._data.get("tracks").get("items")
            if track.get("track").get("id") not in tracks
        ]

    def clear(self):
        self._spotify.playlist_remove_all_occurrences_of_items(
            self.id, [track.id for track in self.tracks]
        )
        self._data["tracks"]["items"] = []

    @property
    def owner(self) -> Artist:
        return Artist(self._spotify, self._data.get("owner"))

    @property
    def tracks(self) -> List[Track]:
        return [
            Track(track.get("track"), self._spotify)
            for track in self._data.get("tracks").get("items")
        ]

    @property
    def total_tracks(self) -> int:
        return self._data.get("tracks").get("total")

    @property
    def public(self):
        return self._data.get("public")

    @property
    def collaborative(self):
        return self._data.get("collaborative")

    @property
    def description(self):
        return self._data.get("description")

    @property
    def followers(self):
        return self._data.get("followers")

    @property
    def snapshot_id(self):
        return self._data.get("snapshot_id")