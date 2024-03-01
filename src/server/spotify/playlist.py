from logging import getLogger
from typing import List

from spotipy import Spotify

from src.server.spotify.asyncify import asyncify
from src.server.spotify.track import Track
from src.server.spotify.resource import SpotifyResource
from src.server.spotify.artist import Artist
from benedict import BeneDict as benedict

from src.server.spotify.utils import not_none

logger = getLogger("server")


class Playlist(SpotifyResource):
    @staticmethod
    def from_id(spotify: Spotify, id: str):
        return Playlist(spotify, not_none(spotify.playlist(id)))

    def __init__(self, spotify: Spotify, data: dict):
        super().__init__(spotify, lambda: spotify.playlist(self.id), data)

    @asyncify
    def delete(self):
        self._spotify.current_user_unfollow_playlist(self.id)

    @asyncify
    def play(self):
        self._spotify.start_playback(context_uri=self.uri)

    @property
    def name(self) -> str:
        return not_none(self._data.get("name"))

    @asyncify
    def follow(self):
        self._spotify.current_user_follow_playlist(self.id)

    @asyncify
    def unfollow(self):
        self._spotify.current_user_unfollow_playlist(self.id)

    @asyncify
    def set_details(self, name: str | None = None, description: str | None = None):
        self._spotify.playlist_change_details(
            self.id, name=name, description=description
        )
        if name is not None:
            self._data["name"] = name
        if description is not None:
            self._data["description"] = description

    @property
    def images(self) -> List[dict]:
        return not_none(self._data.get("images"))

    def reload(self):
        self._data = benedict(self._spotify.playlist(self.id))

    @asyncify
    def add(self, *tracks: str | Track):
        track_ids = [
            track.id if isinstance(track, Track) else track for track in tracks
        ]
        self._spotify.playlist_add_items(self.id, track_ids)
        logger.info(f"Added {len(track_ids)} tracks to {self.name}")
        self.reload()

    @asyncify
    def remove_tracks(self, tracks: List[str]):
        self._spotify.playlist_remove_all_occurrences_of_items(self.id, tracks)
        self._data["tracks"]["items"] = [
            track
            for track in self._data.get("tracks").get("items")
            if track.get("track").get("id") not in tracks
        ]

    async def clear(self):
        tracks = await self.tracks
        await self.asyncily(
            lambda spot: spot.playlist_remove_all_occurrences_of_items(
                self.id, [track.id for track in tracks]
            )
        )
        self._data["tracks"]["items"] = []
        logger.info(f"Cleared {self.name}")

    @property
    def owner(self) -> Artist:
        return Artist(self._spotify, not_none(self._data.get("owner")))

    @property
    @asyncify
    def tracks(self) -> List[Track]:
        return [
            Track(self._spotify, track.get("track"))
            for track in self._spotify.playlist_tracks(self.id).get("items")
        ]

    @property
    def total_tracks(self) -> int:
        return self.get("tracks").get("total")

    @property
    def public(self):
        return self.get("public")

    @property
    def collaborative(self):
        return self.get("collaborative")

    @property
    def description(self):
        return self.get("description")

    @property
    def followers(self):
        return self.get("followers")

    @property
    def snapshot_id(self):
        return self.get("snapshot_id")
