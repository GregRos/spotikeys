from abc import ABC
from ast import Tuple
from asyncio import AbstractEventLoop, ensure_future, get_event_loop, new_event_loop
import code
from concurrent.futures import thread
from enum import auto
from logging import getLogger
import os
import sys
import threading
import time
import traceback
from typing import Any, Awaitable, Callable, Coroutine
from src.client.received_command import ReceivedCommand
from src.client.ui.display_thread import ActivityDisplay
from src.now_playing import MediaStatus
from src.commanding.commands import Command
from src.commanding.handler import AsyncCommandHandler
from src.commands.commands import MediaCommands

logger = getLogger("client")


def handles(*commands: Command) -> Any:
    def decorator(handler: Any):
        setattr(handler, "handles", [c.code for c in commands])
        return handler

    return decorator


class ClientCommandHandler(AsyncCommandHandler[ReceivedCommand, None]):
    _current: ReceivedCommand | None = None
    _lock = threading.Lock()
    _display = ActivityDisplay()
    _mapping: dict[str, AsyncCommandHandler[ReceivedCommand, None]] = {}

    def __init__(
        self,
        loop: AbstractEventLoop,
        downstream: AsyncCommandHandler[Command, MediaStatus],
    ) -> None:
        self._loop = loop

        def with_logging(x):
            logger.info(f"Sending {x} to server")
            return downstream(x)

        self._downstream = with_logging
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
    async def _show_status(self, r_command: ReceivedCommand) -> None:
        try:
            self._display.run(lambda tt: tt.notify_show_status(), auto_hide=False)
            result = await self._downstream(MediaCommands.get_status)
            if self._current:
                self._display.run(
                    lambda tt: tt.notify_show_status(result), auto_hide=True
                )
        except Exception as e:
            self._handle_error(r_command, e)

    @handles(MediaCommands.exit)
    async def _exit(self, r_command: ReceivedCommand) -> None:
        logger.fatal("Exit received! Goodbye.")
        os._exit(0)

    @handles(MediaCommands.hide_status)
    async def _hide_status(self, r_command: ReceivedCommand) -> None:
        self._display.run(lambda tt: tt.hide())

    def _diagnose(self, exception: Exception) -> tuple[str, str]:
        stringified = str(exception)
        if "Restriction violated" in stringified:
            return ("Restriction violated", "⛔")
        return (stringified, "❌")

    def _handle_error(
        self, command: ReceivedCommand, error: Exception
    ) -> MediaStatus | None:
        message, emoji = self._diagnose(error)
        traceback.print_exc()
        self._display.run(
            lambda tt: tt.notify_command_errored(command.command, message, emoji)
        )

    async def _wrap_downstream(self, received: ReceivedCommand, command: Command):
        try:
            self._display.run(lambda tt: tt.notify_command_start(received), False)
            start = time.time()
            result = await self._downstream(command)
            elapsed = time.time() - start
            self._display.run(
                lambda tt: tt.notify_command_done(received, elapsed, result)
            )
        except Exception as e:
            self._handle_error(received, e)

    def _get_handler(self, command: ReceivedCommand) -> Awaitable[None]:
        local_handler = self._mapping.get(command.command.code, None)
        if local_handler:
            return local_handler(command)
        return self._wrap_downstream(command, command.command)

    def _exec(self, command: ReceivedCommand) -> None:
        loop = self._loop
        try:
            handler = self._get_handler(command)
            loop.run_until_complete(handler)

        except RuntimeError as e:
            if "Event loop stopped before Future completed" in str(e):
                logger.warn(f"Event loop stopped before {command} completed.")
                loop.close()
                return

            raise
        else:
            self._current = None

    def __call__(self, command: ReceivedCommand) -> None:
        with self._lock:
            match self._current and self._current.command:
                case Command(code="show_status"):
                    match command.command:
                        case Command(code="show_status"):
                            logger.warn("Already showing status. Ignoring.")
                            return
                        case _:
                            logger.info(
                                f"Received {command} while showing status. Cancelling display."
                            )
                            self._loop.stop()
                            self._loop = new_event_loop()
                            self._current = None
                case None:
                    pass
                case _:
                    logger.error(f"Busy with {self._current}.")
                    return self.busy(command)

            self._current = command
            threading.Thread(target=self._exec, args=(command,)).start()
