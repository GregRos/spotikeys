from asyncio import AbstractEventLoop, new_event_loop
from logging import getLogger
import os
import threading
import time
import traceback
from typing import Any, Awaitable, Callable

from src.client.kb.triggered_command import FailedCommand, TriggeredCommand
from src.client.ui.display_thread import ActivityDisplay
from src.client.volume import ClientVolumeControl
from src.now_playing import MediaStatus
from src.commanding.commands import Command, ParamterizedCommand
from src.commanding.handler import AsyncCommandHandler, handles
from src.commands.media_commands import MediaCommands

logger = getLogger("client")


class ClientCommandHandler(AsyncCommandHandler[TriggeredCommand, None]):
    _current: TriggeredCommand | None = None
    _lock = threading.Lock()
    _display = ActivityDisplay()
    _last_command: TriggeredCommand | None = None

    def __init__(
        self,
        loop: AbstractEventLoop,
        downstream: AsyncCommandHandler[Command, Awaitable[MediaStatus]],
    ) -> None:
        self._loop = loop
        self._volume_control = ClientVolumeControl()

        async def with_logging(x):
            logger.info(f"Sending {x} to server")
            result = await downstream(x)
            if x.code != "get_volume":
                result.volume = self._volume_control.info
            return result

        self._downstream = with_logging

    def busy(self, command: TriggeredCommand) -> None:
        pass

    @handles(MediaCommands.show_status)
    async def _show_status(self, r_command: TriggeredCommand) -> None:
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
    async def _exit(self, r_command: TriggeredCommand) -> None:
        logger.fatal("Exit received! Goodbye.")
        os._exit(0)

    @handles(MediaCommands.hide_status)
    async def _hide_status(self, r_command: TriggeredCommand) -> None:
        self._display.run(lambda tt: tt.hide())

    async def _set_volume(self, r_command: TriggeredCommand, volume: int) -> None:
        self._volume_control.volume = volume
        self._display.run(
            lambda tt: tt.notify_volume_changed(self._volume_control.info)
        )

    @handles(MediaCommands.volume_up)
    async def _volume_up(self, r_command: TriggeredCommand) -> None:
        self._volume_control.volume += 20
        self._display.run(
            lambda tt: tt.notify_volume_changed(self._volume_control.info)
        )

    @handles(MediaCommands.volume_down)
    async def _volume_down(self, r_command: TriggeredCommand) -> None:
        self._volume_control.volume -= 20
        self._display.run(
            lambda tt: tt.notify_volume_changed(self._volume_control.info)
        )

    @handles(MediaCommands.volume_mute)
    async def _volume_mute(self, r_command: TriggeredCommand) -> None:
        self._volume_control.mute = not self._volume_control.mute
        self._display.run(
            lambda tt: tt.notify_volume_changed(self._volume_control.info)
        )

    @handles(MediaCommands.volume_reset)
    async def _volume_reset(self, r_command: TriggeredCommand) -> None:
        playback = await self._downstream(MediaCommands.get_volume)
        vc = self._volume_control
        product = (playback.volume.volume * vc.volume) // 100
        vc.volume = product
        await self._wrap_downstream(r_command)

    def _diagnose(self, exception: Exception) -> tuple[str, str]:
        stringified = str(exception)
        if "Restriction violated" in stringified:
            return ("Restriction violated", "⛔")
        if "VOLUME_CONTROL_DISALLOW" in stringified:
            return ("No volume control", "🔇")
        return (stringified, "❌")

    def _handle_error(
        self, command: TriggeredCommand, error: Exception
    ) -> MediaStatus | None:
        message, emoji = self._diagnose(error)
        traceback.print_exc()
        self._display.run(
            lambda tt: tt.notify_command_errored(command.command, message, emoji)
        )

    async def _wrap_downstream(self, received: TriggeredCommand):
        try:
            command = received.command
            self._display.run(lambda tt: tt.notify_command_start(received), False)
            result = await received.execute_async(lambda: self._downstream(command))
            if result.success:
                self._display.run(lambda tt: tt.notify_command_done(result))
        except Exception as e:
            self._handle_error(received, e)

    def _get_handler(self, command: TriggeredCommand) -> Awaitable[None] | None:
        local_handler = self.get_handler(command)
        if local_handler:
            logger.info(f"Handling {command} locally.")
            return local_handler(command)
        logger.info(f"Passing {command} downstream.")
        return self._wrap_downstream(command)

    def _exec(self, command: TriggeredCommand) -> None:
        loop = self._loop
        try:
            handler = self._get_handler(command)
            if handler:
                loop.run_until_complete(handler)

        except RuntimeError as e:
            if "Event loop stopped before Future completed" in str(e):
                logger.warn(f"Event loop stopped before {command} completed.")
                loop.close()
                return

            raise
        else:
            self._current = None

    def __call__(self, command: TriggeredCommand) -> None:
        with self._lock:
            if (
                self._last_command
                and command.timestamp - self._last_command.timestamp < 0.25
            ):
                return
            self._last_command = command
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
