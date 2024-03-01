from spotipy import Spotify

from src.server.spotify.asyncify import asyncify
from src.server.spotify.resource import SpotifyResource


class Artist(SpotifyResource):
    @staticmethod
    def from_id(spotify: Spotify, id):
        return Artist(spotify, spotify.artist(id))

    def __init__(self, spotify, data: dict | None):
        super().__init__(spotify, lambda: spotify.artist(self.id), data)

    @property
    def genres(self):
        return self._data.get("genres")

    @property
    @asyncify
    def popularity(self):
        return self._data.get("popularity")

    @asyncify
    def follow(self):
        self._spotify.user_follow_artists(self.id)

    @asyncify
    def play(self):
        self._spotify.start_playback(context_uri=self.uri)

    async def unsave(self):
        if not await self.is_saved:
            return False

        await self.asyncily(lambda spot: spot.user_unfollow_artists([self.id]))
        return True

    async def set_saved(self, saved: bool):
        if saved:
            await self.save()
        else:
            await self.unsave()

    @property
    @asyncify
    def is_saved(self):
        return self._spotify.current_user_following_artists(ids=[self.id])

    async def save(self):
        if await self.is_saved:
            return False

        await self.asyncily(lambda spot: spot.user_follow_artists([self.id]))
        return True
