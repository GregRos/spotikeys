from threading import Event
from typing import override

from commanding.handler import CommandHandler

from src.commands import *
from spotify.root import Root


class MediaControlServer(CommandHandler[Code]):
    _root: Root
    _cancel_flag = Event()

    def pop_cancel(self):
        is_set = self._cancel_flag.is_set()
        self._cancel_flag.clear()
        return is_set

    def __init__(self, root: Root):

        self._root = root

    def _get_media(self):
        return "x"

    @override(super().default_response)
    def default_response(self):
        return self._get_media()

    @super().register(cmd_seek_fwd)
    def _seek_fwd(self):
        self._root.player.progress += 30

    @super().register(cmd_seek_bwd)
    def _seek_bwd(self):
        self._root.player.progress -= 30

    @super().register(cmd_play_pause)
    def _play_pause(self):
        self._root.player.play_pause()

    @super().register(cmd_volume_up)
    def _volume_up(self):
        self._root.player.volume += 10

    @super().register(cmd_volume_down)
    def _volume_down(self):
        self._root.player.volume -= 10

    @super().register(cmd_volume_mute)
    def _volume_mute(self):
        print("Mute")

    @super().register(cmd_cancel)
    def _cancel(self):
        self._root.player.cancel()

    @super().register(cmd_love)
    def _love(self):
        track = self._root.player.track
        track.save()
        track.album.save()
        track.artists[0].save()

    @super().register(cmd_prev_track)
    def _prev_track(self):
        self._root.player.prev_track()

    @super().register(cmd_next_track)
    def _next_track(self):
        self._root.player.next_track()

    @super().register(cmd_loop_track)
    def _loop_track(self):
        self._root.player.repeat = "track"
        self._root.player.progress = 0

    @super().register(cmd_get_status)
    def _get_status(self):
        print(self._root.player.track)

    @super().register(cmd_undo)
    def _undo(self):
        print("Undo")

    @super().register(cmd_redo)
    def _redo(self):
        print("Redo")

    @super().register(cmd_spin_this_in_last)
    def _spin_this_in_last(self):
        print("Spin this in last")

    @super().register(cmd_spin_this_in_new)
    def _spin_this_in_new(self):
        print("Spin this in new")

    @super().register(cmd_get_status)
    def _get_status(self):
        print(self._root.player.track)
