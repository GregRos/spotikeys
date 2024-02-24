from threading import Thread, Event
from typing import Callable, Any

from src.commands import *
from spotify.root import Root


class BusyError(Exception):
    def __init__(self, command: Command[Code]):
        super().__init__(f"Command {command} is still being handled.")
        self.command = command


class NoHandlerError(Exception):
    def __init__(self, command: Command[Code]):
        super().__init__(f"No handler for {command}")
        self.command = command


class LocalCommandError(Exception):
    def __init__(self, command: Command[Code]):
        super().__init__(
            f"Command {command} is local and cannot be handled by the server"
        )
        self.command = command


class CommandHandler[Code: str]:
    _root: Root
    _handlers: dict[Code, Callable[[Command[Code]], Any]] = {}
    _current: Command[Code] | None = None
    _cancel_flag = Event()

    def __init__(self, root: Root):
        self._root = root

    def pop_cancel(self):
        is_set = self._cancel_flag.is_set()
        self._cancel_flag.clear()
        return is_set

    def receive(self, command: Command[Code]):
        handler = self._handlers.get(command.code)
        if command.is_local:
            raise LocalCommandError(command)
        if not handler:
            raise NoHandlerError(command)

        if self._current:
            raise BusyError(self._current)

        self._current = command
        return_value = handler(command)
        self._current = None
        return return_value or self._get_media()

    def _get_media(self):
        return "x"

    def _register(self, command: Command):
        if command.is_local:
            raise ValueError(
                f"Command {command} is local and cannot be handled by the server"
            )

        def decorator(callback: Callable[[Command[Code]], Any]):
            if command.code in self._handlers:
                raise ValueError(f"Handler for {command} already exists")

            self._handlers[command.code] = callback
            return callback

        return decorator

    @_register(cmd_seek_fwd)
    def _seek_fwd(self):
        self._root.player.progress += 30

    @_register(cmd_seek_bwd)
    def _seek_bwd(self):
        self._root.player.progress -= 30

    @_register(cmd_play_pause)
    def _play_pause(self):
        self._root.player.play_pause()

    @_register(cmd_volume_up)
    def _volume_up(self):
        self._root.player.volume += 10

    @_register(cmd_volume_down)
    def _volume_down(self):
        self._root.player.volume -= 10

    @_register(cmd_volume_mute)
    def _volume_mute(self):
        print("Mute")

    @_register(cmd_cancel)
    def _cancel(self):
        self._root.player.cancel()

    @_register(cmd_love)
    def _love(self):
        track = self._root.player.track
        track.save()
        track.album.save()
        track.artists[0].save()

    @_register(cmd_prev_track)
    def _prev_track(self):
        self._root.player.prev_track()

    @_register(cmd_next_track)
    def _next_track(self):
        self._root.player.next_track()

    @_register(cmd_loop_track)
    def _loop_track(self):
        self._root.player.repeat = "track"
        self._root.player.progress = 0

    @_register(cmd_get_status)
    def _get_status(self):
        print(self._root.player.track)

    @_register(cmd_undo)
    def _undo(self):
        print("Undo")

    @_register(cmd_redo)
    def _redo(self):
        print("Redo")

    @_register(cmd_spin_this_in_last)
    def _spin_this_in_last(self):
        print("Spin this in last")

    @_register(cmd_spin_this_in_new)
    def _spin_this_in_new(self):
        print("Spin this in new")

    @_register(cmd_get_status)
    def _get_status(self):
        print(self._root.player.track)
