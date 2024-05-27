import asyncio
from functools import partial
import inspect
from logging import getLogger
from os import PathLike
import socket
from threading import Event
import time
from typing import Any, Awaitable, override
from src.commanding.handler import AsyncCommandHandler, handles
from client.volume import VolumeInfo
from src.commanding.commands import ParamterizedCommand
from src.spotify.now_playing import MediaStatus
from src.commanding import Command
from server.errors import NoHandlerError
from server.history import PersistentCommandHistory

from src.commands import *
from server.launcher import is_spotify_running, start_spotify
from src.spotify import Root, playback
from src.spotify.root import SpotifyAuth
from server.history.undo import UndoWaiter


logger = getLogger("server")


class NoPlaybackError(Exception):
    def __init__(self):
        super().__init__("Nothing is playing right now.")


class MediaCommandHandler(AsyncCommandHandler[Command, Awaitable[MediaStatus]]):
    cancel_flag = Event()
    _last_volume = 0
    _root: Root | None = None
    _current: Command | None = None

    def __init__(self, auth: SpotifyAuth, history_file: PathLike):
        super().__init__()
        self._auth = auth
        self.history = PersistentCommandHistory(history_file, media_commands)

    @property
    def root(self):
        if not self._root:
            logger.info("No connected Spotify root. Creating...")
            self._root = Root(self._auth)
        return self._root

    def undoable(self, command: Command):
        return UndoWaiter(self.history, command)

    def exec(self, command: Command):
        self.history.push(command)

    def pop_cancel(self):
        is_set = self.cancel_flag.is_set()
        return is_set

    @handles(MediaCommands.set_playlist)
    async def _set_playlist(self, args: SetPlaylistArgs):
        playlist = await self.root.playlist(args["id"])
        await playlist.set_details(name=args["name"], description=args["description"])
        await playlist.add(*args["tracks"])

    @handles(MediaCommands.exit)
    async def _exit(self):
        raise ValueError("Local command exit!")

    @property
    async def playing(self) -> playback.Playback:
        match await self.root.playback:
            case None:
                raise NoPlaybackError()
            case playback if playback is not None:
                return playback
            case _:
                raise ValueError("Unexpected playback type")

    @handles(MediaCommands.seek_to)
    async def _seek_to(self, to: float):
        playing = await self.playing
        await playing.set_progress(to)

    @handles(MediaCommands.repeat_to)
    async def _repeat_to(self, repeat: playback.Repeat):
        playing = await self.playing
        await playing.set_repeat(repeat)

    @handles(MediaCommands.delete_playlist)
    async def _delete_playlist(self, playlist_id: str):
        playlist = await self.root.playlist(playlist_id)
        await playlist.delete()

    @handles(MediaCommands.seek_fwd)
    async def _seek_fwd(self):
        playing = await self.playing
        cur_progress = playing.progress
        with self.undoable(MediaCommands.seek_to(cur_progress)):
            await playing.set_progress(cur_progress + 30)
            return playing.get_status()

    @handles(MediaCommands.seek_bwd)
    async def _seek_bwd(self):
        playing = await self.playing
        cur_progress = playing.progress
        with self.undoable(MediaCommands.seek_to(cur_progress)):
            await playing.set_progress(cur_progress - 30)
            return playing.get_status()

    @handles(MediaCommands.play)
    async def _play(self):
        playing = await self.playing
        await playing.play()

    @handles(MediaCommands.pause)
    async def _pause(self):
        playing = await self.playing
        await playing.pause()

    @handles(MediaCommands.play_pause)
    async def _play_pause(self):
        playback = await self.root.playback
        if not playback:
            await self._transfer_to_current()
        playing = await self.playing
        if playing.is_playing:
            with self.undoable(MediaCommands.play):
                await playing.pause()
        else:
            with self.undoable(MediaCommands.pause):
                await playing.play()

    @handles(MediaCommands.volume_up)
    async def _volume_up(self):
        playing = await self.playing
        old_volume = playing.volume
        with self.undoable(MediaCommands.volume_to(old_volume)):
            await playing.set_volume(min(100, old_volume + 20))

    @handles(MediaCommands.volume_down)
    async def _volume_down(self):
        playing = await self.playing
        old_volume = playing.volume
        with self.undoable(MediaCommands.volume_to(old_volume)):
            await playing.set_volume(max(0, old_volume - 20))

    @handles(MediaCommands.volume_mute)
    async def _volume_mute(self):
        playing = await self.playing
        old_volume = playing.volume
        with self.undoable(MediaCommands.volume_to(old_volume)):
            if old_volume == 0:
                await playing.set_volume(self._last_volume)
            else:
                self._last_volume = old_volume
                await playing.set_volume(0)
            return playing.get_status()

    @handles(MediaCommands.get_volume)
    def _get_volume(self):
        return self._get_status()

    @handles(MediaCommands.volume_reset)
    async def _volume_reset(self):
        playing = await self.playing
        old_volume = playing.volume
        with self.undoable(MediaCommands.volume_to(old_volume)):
            await playing.set_volume(100)
            return playing.get_status()

    @handles(MediaCommands.cancel)
    async def _cancel(self):
        print("Cancel")

    @handles(MediaCommands.set_love_state)
    async def _set_love_state(self, args: LoveStateArgs):
        track = await self.root.track(args["id"])
        album = track.album
        artist = track.artists[0]
        coroutines = [
            track.set_saved(args["track_love"]),
            album.set_saved(args["album_love"]) if album else None,
            artist.set_saved(args["artist_love"]),
        ]
        await asyncio.gather(*[c for c in coroutines if c])

    @handles(MediaCommands.love)
    async def _love(self):
        async def maybe_love_album(album):
            if album:
                return False
            return await album.save()

        playing = await self.playing
        track = playing.track
        all_artist_changes = track.artists[0].save()
        coroutines = [
            track.save(),
            maybe_love_album(track.album),
            all_artist_changes,
        ]
        track_change, album_change, artist_change = await asyncio.gather(*coroutines)
        self.history.push(
            MediaCommands.set_love_state(
                {
                    "album_love": not album_change,
                    "artist_love": not artist_change,
                    "id": track.id,
                    "track_love": not track_change,
                }
            )
        )

    @handles(MediaCommands.prev_track)
    async def _prev_track(self):
        playing = await self.playing
        with self.undoable(MediaCommands.next_track):
            await playing.prev_track()
            return playing.get_status()

    @handles(MediaCommands.transfer_to_device)
    async def _transfer_to_device(self, device: str | Device):
        device = device.id if isinstance(device, Device) else device
        playing = await self.playing
        with self.undoable(MediaCommands.transfer_to_device(playing.device)):
            await self.root.transfer_playback(device)
            return playing.get_status()

    @handles(MediaCommands.transfer_to_phone)
    async def _transfer_to_phone(self):
        playing = await self.root.playback
        if not playing:
            raise NoPlaybackError()
        devices = await self.root.get_devices()
        logger.debug(f"Got devices: {", ".join(d.name for d in devices)}")
        phone = next(d for d in devices if d.type == "Smartphone")
        logger.debug(f"Phone: {phone.name}")
        if playing:
            self.history.push(MediaCommands.transfer_to_device(playing.device))
        await self.root.transfer_playback(phone)
        return playing.get_status()

    @handles(MediaCommands.transfer_to_current)
    async def _transfer_to_current(self):
        playing = await self.root.playback

        devices = await self.root.get_devices()
        hostname = socket.gethostname()
        logger.debug(f"Got devices: {", ".join(d.name for d in devices)}")
        logger.debug(f"Current device: {hostname}")
        if playing:
            self.history.push(MediaCommands.transfer_to_device(playing.device))
        try:
            current_device = next(
                d for d in devices if d.name.lower() == hostname.lower()
            )
        except StopIteration as e:
            if is_spotify_running():
                raise ValueError(
                    "Spotify is running but device not found. Something is wrong."
                )
            else:
                start_spotify()
                time.sleep(5)
                devices = await self.root.get_devices()
                current_device = next(
                    d for d in devices if d.name.lower() == hostname.lower()
                )
        await self.root.transfer_playback(current_device)
        playing = await self.root.playback
        return playing.get_status()  # type: ignore

    @handles(MediaCommands.next_track)
    async def _next_track(self):
        playing = await self.playing
        devices = await self.root.get_devices()
        with self.undoable(MediaCommands.prev_track):
            await playing.next_track()
            return playing.get_status()

    @handles(MediaCommands.loop_track)
    async def _loop_track(self):
        playing = await self.playing
        with self.undoable(MediaCommands.repeat_to(playing.repeat)):
            await playing.set_repeat("track")
            await playing.set_progress(0)
            return playing.get_status()

    @handles(MediaCommands.undo)
    def _undo(self):
        print("Undo")

    @handles(MediaCommands.redo)
    def _redo(self):
        print("Redo")

    @handles(MediaCommands.spin_this_in_last)
    async def _spin_this_in_last(self):
        playing = await self.playing
        track = playing.track
        recommended, playlists = await asyncio.gather(
            track.recommend(),
            self.root.me.playlists.items(),
        )
        autogenerated = [pl for pl in playlists if pl.name.startswith("🤖")][0]
        logger.info(f"Found {autogenerated.name}")
        if autogenerated.total_tracks < 100:
            self.history.push(
                MediaCommands.set_playlist(
                    {
                        "id": autogenerated.id,
                        "name": autogenerated.name,
                        "tracks": [t.id for t in await autogenerated.tracks],
                        "description": autogenerated.description,
                    }
                )
            )
            logger.info("Saved previous playlist state")
        else:
            self.history.not_undoable("Playlist too large. Not saving.")
        await autogenerated.clear()
        await autogenerated.add(*recommended)
        await autogenerated.play()
        return await self._get_status()

    @handles(MediaCommands.delete_current_playlist)
    async def _delete_current_playlist(self):
        playing = await self.playing
        match playing._data:
            case {
                "context": {
                    "type": "playlist",
                    "uri": playlist_uri,
                }
            }:
                playlist = await self.root.playlist(playlist_uri)
                await playlist.delete()
            case {
                "context": {
                    "type": something_else,
                }
            }:
                raise ValueError(f"Playing a {something_else}, not a playlist!")

    @handles(MediaCommands.spin_this_in_new)
    async def _spin_this_in_new(self):
        playing = await self.playing
        track = playing.track
        recommending = track.recommend()
        creating_playlist = self.root.me.playlists.add(
            f"🤖 {track.artists_string} – {track.name}",
            description="Auto-generated.",
        )

        recommended, playlist = await asyncio.gather(recommending, creating_playlist)
        undo_command = MediaCommands.delete_playlist(playlist.id)
        self.history.push(undo_command)
        await playlist.add(*recommended)
        await playlist.play()
        return await self._get_status()

    @handles(MediaCommands.get_status)
    async def _get_status(self):
        playing = await self.playing
        return playing.get_status()

    @handles(MediaCommands.volume_to)
    async def _volume_to(self, volume: int):
        playing = await self.playing
        await playing.set_volume(volume)

    @handles(MediaCommands.rewind_this)
    async def _rewind_this(self):
        playing = await self.playing
        old_repeat = playing.repeat
        await playing.set_repeat(False)
        count = False
        try:
            while True:
                await playing.prev_track()
                count += 1
        except Exception as e:
            if "Restriction violated" in str(e) and count > 0:
                return count
            raise
        finally:
            await playing.set_repeat(old_repeat)
            return playing.get_status()

    @handles(MediaCommands.next_multi)
    def _next_multi(self):
        print("Next multi")

    @handles(MediaCommands.prev_multi)
    def _prev_multi(self):
        print("Prev multi")

    @handles(MediaCommands.show_status)
    def _show_status(self):
        raise NotImplementedError("Local command only.")

    @handles(MediaCommands.hide_status)
    def _hide_status(self):
        raise NotImplementedError("Local command only.")

    async def get_media(self):
        if playback := await self.root.playback:
            return playback.get_status()

    async def handle(self, command: Command) -> MediaStatus | None:
        handler: Any = self.get_handler(command)

        if not handler:
            raise NoHandlerError(command)

        if command is ParamterizedCommand:
            handler = partial(handler, command.arg)
        try:
            match command:
                case ParamterizedCommand(arg):
                    result = await handler(arg)
                case Command():
                    if inspect.signature(handler).parameters.__len__() == 0:
                        result = await handler()
                    else:
                        result = await handler(command)
            result = result or await self.get_media()
            logger.info(f"Executed {command}, received {result}")
            return result
        finally:
            self._current = None

    async def __call__(self, command: Command) -> MediaStatus:
        logger.info(f"Received command: {command}")

        start = time.time()
        result = await self.handle(command)
        if result:
            result.volume = VolumeInfo(result.volume.volume, False)
        elapsed = time.time() - start

        logger.info(f"Command {command} took {elapsed:.3f} seconds")
        return result  # type: ignore
