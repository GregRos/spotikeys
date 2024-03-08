from ast import Param
import asyncio
from functools import partial
from logging import getLogger, root
from os import PathLike
import os
from pathlib import Path
import socket
from threading import Event
import time
from typing import override
from src.commanding.commands import ParamterizedCommand
from src.now_playing import MediaStatus
from src.commanding import Command
from src.commanding.handler import PropertyBasedCommandHandler
from src.server.errors import BusyError, NoHandlerError
from src.server.history import PersistentCommandHistory

from src.commands import *
from src.server.launcher import is_spotify_running, start_spotify
from src.server.spotify import Root, album, device, playback, track
from src.server.spotify.root import SpotifyAuth
from src.server.history.undo import UndoWaiter


logger = getLogger("server")
def get_system_volume():
    sessions = AudioUtilities.GetAllSessions()
    for session in sessions:
        if session.Process and session.Process.name() == "SystemSounds.exe":
            volume = session.SimpleAudioVolume
            return volume.GetMasterVolume() * 100  # Convert to percentage


class NoPlaybackError(Exception):
    def __init__(self):
        super().__init__("Nothing is playing right now.")


class MediaCommandHandler(MediaCommands):
    cancel_flag = Event()
    _last_volume = 0
    _root: Root | None = None
    _current: Command | None = None

    def __init__(self, auth: SpotifyAuth, history_file: PathLike):
        self._auth = auth
        self.history = PersistentCommandHistory(history_file, commands)

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

    @override
    async def set_playlist(self, args: SetPlaylistArgs):
        playlist = await self.root.playlist(args["id"])
        await playlist.set_details(name=args["name"], description=args["description"])
        await playlist.add(*args["tracks"])

    @override
    async def exit(self):
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

    @override
    async def seek_to(self, to: float):
        playing = await self.playing
        await playing.set_progress(to)

    @override
    async def repeat_to(self, repeat: playback.Repeat):
        playing = await self.playing
        await playing.set_repeat(repeat)

    @override
    async def delete_playlist(self, playlist_id: str):
        playlist = await self.root.playlist(playlist_id)
        await playlist.delete()

    @override
    async def seek_fwd(self):
        playing = await self.playing
        cur_progress = playing.progress
        with self.undoable(MediaCommands.seek_to(cur_progress)):
            await playing.set_progress(cur_progress + 30)
            return playing.get_status()

    @override
    async def seek_bwd(self):
        playing = await self.playing
        cur_progress = playing.progress
        with self.undoable(MediaCommands.seek_to(cur_progress)):
            await playing.set_progress(cur_progress - 30)
            return playing.get_status()

    @override
    async def play(self):
        playing = await self.playing
        await playing.play()

    @override
    async def pause(self):
        playing = await self.playing
        await playing.pause()

    @override
    async def play_pause(self):
        playback = await self.root.playback
        if not playback:
            await self.transfer_to_current()
        playing = await self.playing
        if playing.is_playing:
            with self.undoable(MediaCommands.play):
                await playing.pause()
        else:
            with self.undoable(MediaCommands.pause):
                await playing.play()

    @override
    async def volume_up(self):
        playing = await self.playing
        old_volume = playing.volume
        with self.undoable(MediaCommands.volume_to(old_volume)):
            await playing.set_volume(min(100, old_volume + 20))

    @override
    async def volume_down(self):
        playing = await self.playing
        old_volume = playing.volume
        with self.undoable(MediaCommands.volume_to(old_volume)):
            await playing.set_volume(max(0, old_volume - 20))

    @override
    async def volume_mute(self):
        playing = await self.playing
        old_volume = playing.volume
        with self.undoable(MediaCommands.volume_to(old_volume)):
            if old_volume == 0:
                await playing.set_volume(self._last_volume)
            else:
                self._last_volume = old_volume
                await playing.set_volume(0)
            return playing.get_status()

    @override
    async def volume_max(self):
        playing = await self.playing
        old_volume = playing.volume
        with self.undoable(MediaCommands.volume_to(old_volume)):
            await playing.set_volume(100)
            return playing.get_status()

    @override
    def cancel(self):
        print("Cancel")

    @override
    async def set_love_state(self, args: LoveStateArgs):
        track = await self.root.track(args["id"])
        album = track.album
        artist = track.artists[0]
        coroutines = [
            track.set_saved(args["track_love"]),
            album.set_saved(args["album_love"]) if album else None,
            artist.set_saved(args["artist_love"]),
        ]
        await asyncio.gather(*[c for c in coroutines if c])

    @override
    async def love(self):
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

    @override
    async def prev_track(self):
        playing = await self.playing
        with self.undoable(MediaCommands.next_track):
            await playing.prev_track()
            return playing.get_status()

    @override
    async def transfer_to_device(self, device: str | Device):
        device = device.id if isinstance(device, Device) else device
        playing = await self.playing
        with self.undoable(MediaCommands.transfer_to_device(playing.device)):
            await self.root.transfer_playback(device)
            return playing.get_status()

    @override
    async def transfer_to_phone(self):
        playing = await self.root.playback
        devices = await self.root.get_devices()
        logger.debug(f"Got devices: {", ".join(d.name for d in devices)}")
        phone = next(d for d in devices if d.type == "Smartphone")
        logger.debug(f"Phone: {phone.name}")
        if playing:
            self.history.push(MediaCommands.transfer_to_device(playing.device))
        await self._root.transfer_playback(phone)
        return playing.get_status()

    @override
    async def transfer_to_current(self):
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
        return playing.get_status()

    @override
    async def next_track(self):
        playing = await self.playing
        devices = await self.root.get_devices()
        with self.undoable(MediaCommands.prev_track):
            await playing.next_track()
            return playing.get_status()

    @override
    async def loop_track(self):
        playing = await self.playing
        with self.undoable(MediaCommands.repeat_to(playing.repeat)):
            await playing.set_repeat("track")
            return playing.get_status()

    @override
    def undo(self):
        print("Undo")

    @override
    def redo(self):
        print("Redo")

    @override
    async def spin_this_in_last(self):
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
        return await self.get_status()

    @override
    async def delete_current_playlist(self):
        playing = await self.playing
        match playing._data:
            case {
                "context": {
                    "type": "playlist",
                    "uri": playlist_uri,
                }
            }:
                playlist = await self._root.playlist(playlist_uri)
                await playlist.delete()
            case {
                "context": {
                    "type": something_else,
                }
            }:
                raise ValueError(f"Playing a {something_else}, not a playlist!")

    @override
    async def spin_this_in_new(self):
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
        return await self.get_status()

    @override
    async def get_status(self):
        playing = await self.playing
        return playing.get_status()

    @override
    async def volume_to(self, volume: int):
        playing = await self.playing
        await playing.set_volume(volume)

    @override
    async def rewind_this(self):
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

    @override
    def next_multi(self):
        print("Next multi")

    @override
    def prev_multi(self):
        print("Prev multi")

    @override
    def show_status(self):
        raise NotImplementedError("Local command only.")

    @override
    def hide_status(self):
        raise NotImplementedError("Local command only.")

    async def get_media(self):
        if playback := await self.root.playback:
            return MediaStatus(
                title=playback.track.name,
                artist=playback.track.artists[0].name,
                album=playback.track.album.name,
                duration=playback.track.duration,
                position=playback.progress,
                is_playing=playback.is_playing,
            )

    async def handle(self, command: Command) -> MediaStatus | None:
        handler = getattr(self, command.code, None)

        if not handler:
            raise NoHandlerError(command)

        if command is ParamterizedCommand:
            handler = partial(handler, command.arg)
        try:
            match command:
                case ParamterizedCommand(arg):
                    result = await handler(arg)
                case Command():
                    result = await handler()
            return result or await self.get_media()
        finally:
            self._current = None

    async def __call__(self, command: Command) -> MediaStatus:
        logger.info(f"Received command: {command}")

        start = time.time()
        result = await self.handle(command)
        elapsed = time.time() - start
        logger.info(f"Command {command} took {elapsed:.3f} seconds")
        return result  # type: ignore
