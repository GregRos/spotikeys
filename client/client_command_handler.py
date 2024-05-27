from asyncio import AbstractEventLoop, new_event_loop
from logging import getLogger
import os
import threading
import time
import traceback
from typing import Any, Awaitable, Callable

from client.media_types import MediaStageMessage
from src.kb.triggered_command import FailedCommand, OkayCommand, TriggeredCommand
from client.floating_tooltip import ActionHUD
from src.ui.model.context import Ctx
from src.ui import WindowMount
from client.volume import ClientVolumeControl, VolumeInfo
from src.spotify.now_playing import MediaStatus
from src.commanding.commands import Command, ParamterizedCommand
from src.commanding.handler import AsyncCommandHandler, handles
from src.commands.media_commands import MediaCommands

logger = getLogger("client")


class ClientCommandHandler(AsyncCommandHandler[TriggeredCommand, None]):
    _current: TriggeredCommand | None = None
    _lock = threading.Lock()
    _last_command: TriggeredCommand | None = None
    _root: WindowMount
    _last_status: MediaStatus

    def __init__(
        self,
        loop: AbstractEventLoop,
        downstream: AsyncCommandHandler[Command, Awaitable[MediaStatus]],
    ) -> None:

        super().__init__()
        self._last_status = MediaStatus(
            artist="No one",
            title="Nothing",
            album="N/A",
            volume=VolumeInfo(volume=0, mute=False),
            duration=10,
            position=1,
            is_playing=False,
            device=None,  # type: ignore
        )
        self._root = WindowMount(ActionHUD())
        self._root(
            executed=None,
            last_status=self._last_status,
            hidden=True,
        )
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

    @handles(MediaCommands.exit)
    async def _exit(self, r_command: TriggeredCommand) -> None:
        logger.fatal("Exit received! Goodbye.")
        os._exit(0)

    def set_value(self, thingy: MediaStageMessage) -> None:
        if isinstance(thingy, OkayCommand):
            self._last_status = thingy.result
            self._last_command = thingy.triggered
            self._root(
                hidden=False, executed=thingy, last_status=self._last_status
            ).schedule(lambda _: self._root(hidden=True), 3.0)
        elif isinstance(thingy, TriggeredCommand):
            self._last_command = thingy
        else:
            print(thingy)

    @handles(MediaCommands.show_status)
    async def _show_status(self, r_command: TriggeredCommand) -> None:

        self.set_value(r_command)
        result = await r_command.execute_async(
            lambda: self._downstream(MediaCommands.get_status)
        )
        if self._current:
            self.set_value(result)

    @handles(MediaCommands.hide_status)
    async def _hide_status(self, r_command: TriggeredCommand) -> None:
        self._root(hidden=True)

    @handles(MediaCommands.volume_up)
    async def _volume_up(self, r_command: TriggeredCommand) -> None:
        def handle_volume_up():
            self._last_status.volume = self._volume_control.info
            self._volume_control.volume += 10
            return self._last_status

        exec = r_command.execute(handle_volume_up)
        self.set_value(exec)

    @handles(MediaCommands.volume_down)
    async def _volume_down(self, r_command: TriggeredCommand) -> None:
        def handle_volume_down():
            self._volume_control.volume -= 10
            self._last_status.volume = self._volume_control.info
            return self._last_status

        exec = r_command.execute(handle_volume_down)
        self.set_value(exec)

    @handles(MediaCommands.volume_mute)
    async def _volume_mute(self, r_command: TriggeredCommand) -> None:
        self._volume_control.mute = not self._volume_control.mute

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

    async def _wrap_downstream(self, received: TriggeredCommand):
        command = received.command
        self.set_value(received)
        result = await received.execute_async(lambda: self._downstream(command))
        if isinstance(result, OkayCommand):
            self._last_status = result.result
        self.set_value(result)

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
        if (
            self._last_command
            and command == self._last_command
            and command.timestamp - self._last_command.timestamp < 0.25
        ):
            return
        with self._lock:

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
