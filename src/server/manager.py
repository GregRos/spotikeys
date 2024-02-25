from os import PathLike
from pathlib import Path
from threading import Event
from typing import override

from src.commanding import Command
from src.commanding.handler import CommandHandler
from src.server.history import PersistentCommandHistory

from src.commands import *
from src.server.spotify import Root


class MediaCommandHandler(MediaCommands, CommandHandler):
    root: Root
    cancel_flag = Event()

    def __init__(self, root: Root, history_file: PathLike):
        self.root = root
        self.history = PersistentCommandHistory(history_file, commands)

    def exec(self, command: Command):
        self.history.push(command)

    def pop_cancel(self):
        is_set = self.cancel_flag.is_set()
        self.cancel_flag.clear()
        return is_set

    def get_media(self):
        return "x"

    @override
    def seek_fwd(self):
        self.root.player.progress += 30

    @override
    def seek_bwd(self):
        self.root.player.progress -= 30

    @override
    def play_pause(self):
        self.root.player.play_pause()

    @override
    def volume_up(self):
        self.root.player.volume += 10

    @override
    def volume_down(self):
        self.root.player.volume -= 10

    @override
    def volume_mute(self):
        print("Mute")

    @override
    def volume_max(self):
        self.root.player.volume = 100

    @override
    def cancel(self):
        self.root.player.cancel()

    @override
    def love(self):
        track = self.root.player.track
        track.save()
        track.album.save()
        track.artists[0].save()

    @override
    def prev_track(self):
        self.root.player.prev_track()

    @override
    def next_track(self):
        self.root.player.next_track()

    @override
    def loop_track(self):
        self.root.player.repeat = "track"
        self.root.player.progress = 0

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
        print(self.root.player.track)

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
        print(self.root.player.track)

    @override
    def hide_status(self):
        print("Hide status")

    @override
    def __call__(self, command: Command):
        return super().__call__(command) or self.get_media()
