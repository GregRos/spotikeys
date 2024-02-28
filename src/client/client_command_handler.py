from abc import ABC
import threading
import time
import traceback
from typing import Any, Callable
from src.client.received_command import ReceivedCommand
from src.client.ui.display_thread import ActivityDisplay
from src.client.ui.now_playing import MediaStatus
from src.commanding.commands import Command
from src.commanding.handler import CommandHandler
from src.commands.commands import MediaCommands


def handles(*commands: Command) -> Any:
    def decorator(handler: Any):
        setattr(handler, "handles", [c.code for c in commands])
        return handler

    return decorator


class ClientCommandHandler(CommandHandler[ReceivedCommand, None]):
    _thread: ActivityDisplay
    _current: ReceivedCommand | None = None
    _lock = threading.Lock()
    _display = ActivityDisplay()
    _mapping: dict[str, CommandHandler[ReceivedCommand, None]] = {}

    def __init__(self, downstream: CommandHandler[Command, MediaStatus]) -> None:
        self._downstream = downstream
        for name in dir(self):
            handler = getattr(self, name)
            if not hasattr(handler, "handles"):
                continue

            for code in handler.handles:
                if code in self._mapping:
                    raise ValueError(f"Duplicate handler for {code}")
                self._mapping[code] = handler

    def busy(self, command: ReceivedCommand) -> None:
        pass

    @handles(MediaCommands.show_status)
    def _show_status(self, r_command: ReceivedCommand) -> None:
        status = self._downstream(MediaCommands.get_status)
        try:
            self._display.run(lambda tt: tt.notify_command_done(r_command, 0, status))
        except Exception as e:
            self._handle_error(r_command, e)

    @handles(MediaCommands.hide_status)
    def _hide_status(self, r_command: ReceivedCommand) -> None:
        self._display.run(lambda tt: tt.hide())

    def _handle_error(
        self, command: ReceivedCommand, error: Exception
    ) -> MediaStatus | None:
        traceback.print_exc()
        self._display.run(lambda tt: tt.notify_command_errored(command.command, error))

    def _exec_in_thread(self, command: ReceivedCommand) -> None:
        local_handler = self._mapping.get(command.command.code, None)
        if local_handler:
            return local_handler(command)
        try:
            self._display.run(lambda tt: tt.notify_command_start(command), False)
            start = time.time()
            result = self._downstream(command.command)
            elapsed = time.time() - start
            self._display.run(
                lambda tt: tt.notify_command_done(command, elapsed, result)
            )
        except Exception as e:
            self._handle_error(command, e)
        finally:
            self._current = None

    def __call__(self, command: ReceivedCommand) -> None:
        if self._current:
            return self.busy(command)
        with self._lock:
            self._current = command
            threading.Thread(target=self._exec_in_thread, args=(command,)).start()
