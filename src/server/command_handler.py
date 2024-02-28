from os import PathLike
from pathlib import Path
from threading import Event
from typing import override

from src.client.ui.now_playing import MediaStatus
from src.commanding import Command
from src.commanding.handler import PropertyBasedCommandHandler
from src.server.history import PersistentCommandHistory

from src.commands import *
from src.server.spotify import Root


class NoPlaybackError(Exception):
    def __init__(self):
        super().__init__("Nothing is playing right now.")


class MediaCommandHandler(MediaCommands, PropertyBasedCommandHandler):
    root: Root
    cancel_flag = Event()

    def __init__(self, root: Root, history_file: PathLike):
        super().__init__("media")
        self.root = root
        self.history = PersistentCommandHistory(history_file, commands)

    def exec(self, command: Command):
        self.history.push(command)

    def pop_cancel(self):
        is_set = self.cancel_flag.is_set()
        self.cancel_flag.clear()
        return is_set

    @property
    def expect_playback(self):
        match self.root.playback:
            case None:
                raise NoPlaybackError()
            case playback:
                return playback

    @override
    def seek_fwd(self):
        self.expect_playback.progress += 30

    @override
    def seek_bwd(self):
        self.expect_playback.progress -= 30

    @override
    def play_pause(self):
        if playback := self.root.playback:
            if playback.is_playing:
                playback.pause()
            else:
                playback.play()

    @override
    def volume_up(self):
        self.expect_playback.volume += 10

    @override
    def volume_down(self):
        self.expect_playback.volume -= 10

    @override
    def volume_mute(self):
        print("Mute")

    @override
    def volume_max(self):
        self.expect_playback.volume = 100

    @override
    def cancel(self):
        print("Cancel")

    @override
    def love(self):
        track = self.expect_playback.track
        track.save()
        if album := track.album:
            album.save()
        for artist in track.artists:
            artist.save()

    @override
    def prev_track(self):
        self.expect_playback.prev_track()

    @override
    def next_track(self):
        self.expect_playback.next_track()

    @override
    def loop_track(self):
        match self.root:
            case None:
                self.expect_playback.repeat = "track"
                self.expect_playback.progress = 0

    @override
    def undo(self):
        print("Undo")

    @override
    def redo(self):
        print("Redo")

    @override
    def spin_this_in_last(self):
        print("Spin this in last")

    @override
    def spin_this_in_new(self):
        print("Spin this in new")

    @override
    def get_status(self):
        print(self.expect_playback.track)

    @override
    def rewind_this(self):
        print("Rewind this")

    @override
    def next_multi(self):
        print("Next multi")

    @override
    def prev_multi(self):
        print("Prev multi")

    @override
    def show_status(self):
        print(self.expect_playback.track)

    @override
    def hide_status(self):
        print("Hide status")

    def get_media(self):
        if playback := self.root.playback:
            return MediaStatus(
                title=playback.track.name,
                artist=playback.track.artists[0].name,
                album=playback.track.album.name,
                duration=playback.track.duration,
                position=playback.progress,
            )

    @override
    def __call__(self, command: Command):
        return super().__call__(command) or self.get_media()
