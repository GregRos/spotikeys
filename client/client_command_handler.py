from asyncio import AbstractEventLoop, new_event_loop
from concurrent.futures import ThreadPoolExecutor
from logging import getLogger
import os
import re
import threading
import time
import traceback
from typing import Any, Awaitable, Callable, Iterable
from flask.cli import F
import keyboard
from pyvda import AppView, VirtualDesktop, get_virtual_desktops
from win32api import GetKeyState
from win32con import VK_CAPITAL
from client.desktop.desktop_status import DesktopExec, Pan, Shove
from client.hud import HUD
from client.media.media_types import MediaStageMessage
from src.commands.desktop_commands import DesktopCommands
from src.kb.triggered_command import FailedCommand, OkayCommand, TriggeredCommand
from client.media.media_hud import MediaHUD
from src.ui.model.context import Ctx
from src.ui import WindowMount
from client.media.volume import ClientVolumeControl, VolumeInfo
from src.spotify.now_playing import MediaStatus
from src.commanding.commands import Command, ParamterizedCommand
from src.commanding.handler import AsyncCommandHandler, handles
from src.commands.media_commands import MediaCommands
from pywinauto import WindowSpecification, Application
from pywinauto.win32_element_info import HwndElementInfo


logger = getLogger("client")

pat = re.compile("(\\S*) - Visual Studio Code")


def get_window_substr(hinfo: HwndElementInfo):
    txt = hinfo.name
    if "Visual Studio Code" in txt:
        if proj := pat.search(txt):
            return proj[0]
    return None


def get_info(av: AppView):
    return HwndElementInfo


def get_related_windows(
    av: AppView,
) -> tuple[tuple[HwndElementInfo, ...], tuple[AppView, ...]]:
    def f():
        hinfo = HwndElementInfo(av.hwnd)
        yield hinfo, av
        substr = get_window_substr(hinfo)
        if not substr:
            return []
        proc = hinfo.process_id
        app = Application().connect(process=proc)
        ws = app.windows(title_re=".*" + substr + ".*")
        for i, x in enumerate(ws):
            wrapper = HwndElementInfo(x.handle)
            print(f"Got {i}) {wrapper.rich_text}")
            yield wrapper, AppView(x.handle)

    r = list(f())
    return tuple(map(lambda x: x[0], r)), tuple(map(lambda x: x[1], r))


class ClientCommandHandler(AsyncCommandHandler[TriggeredCommand, None]):
    _current: TriggeredCommand | None = None
    _lock = threading.Lock()
    _root: WindowMount
    _last_media_status: MediaStatus
    _thread_pool = ThreadPoolExecutor(1)

    def __init__(
        self,
        loop: AbstractEventLoop,
        downstream: AsyncCommandHandler[Command, Awaitable[MediaStatus]],
    ) -> None:

        super().__init__()
        self._last_media_status = MediaStatus(
            artist="No one",
            title="Nothing",
            album="N/A",
            volume=VolumeInfo(volume=0, mute=False),
            duration=10,
            position=1,
            is_playing=False,
            device=None,  # type: ignore
        )
        self._root = WindowMount(HUD())
        self._root(
            executed=None,
            last_status=self._last_media_status,
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

    _id = 0

    def set_value(self, thingy: MediaStageMessage | DesktopExec) -> None:
        self._id += 1
        if isinstance(thingy, OkayCommand):
            self._root(
                hidden=False,
                executed=thingy,
                last_status=(
                    thingy.result if isinstance(thingy.result, MediaStatus) else None
                ),
                refresh_id=self._id,
            ).schedule(lambda _: self._root(hidden=True), 3.0)
        elif isinstance(thingy, DesktopExec):
            self._root(hidden=False, executed=thingy, refresh_id=self._id)
        elif isinstance(thingy, TriggeredCommand):
            self._root(hidden=False, executed=thingy, refresh_id=self._id)
        else:
            logger.warn(thingy)
            self._root(
                hidden=False,
                executed=thingy,
                last_status=self._last_media_status,
                refresh_id=self._id,
            ).schedule(lambda _: self._root(hidden=True), 3.0)

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
            self._last_media_status.volume = self._volume_control.info
            self._volume_control.volume += 10
            return self._last_media_status

        exec = r_command.execute(handle_volume_up)
        self.set_value(exec)

    @handles(MediaCommands.volume_down)
    async def _volume_down(self, r_command: TriggeredCommand) -> None:
        def handle_volume_down():
            self._volume_control.volume -= 10
            self._last_media_status.volume = self._volume_control.info
            return self._last_media_status

        exec = r_command.execute(handle_volume_down)
        self.set_value(exec)

    @handles(MediaCommands.volume_mute)
    async def _volume_mute(self, r_command: TriggeredCommand) -> None:

        def handle_volume_mute():
            self._volume_control.mute = not self._volume_control.mute
            self._last_media_status.volume = self._volume_control.info
            return self._last_media_status

        exec = r_command.execute(handle_volume_mute)
        self.set_value(exec)

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
            self._last_media_status = result.result
        self.set_value(result)

    def _get_handler(self, command: TriggeredCommand) -> Awaitable[None] | None:
        local_handler = self.get_handler(command)
        if local_handler:
            if command.command.log:
                logger.info(f"Handling {command} locally.")
            if isinstance(command.command, ParamterizedCommand):
                return local_handler(command.command.arg, command)
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
        except Exception as e:
            traceback.print_exc()
        else:
            self._current = None

    @property
    def current_vd(self):
        return VirtualDesktop.current()

    def get_desktop_at(self, pos: int, loop=False) -> VirtualDesktop:
        total = len(get_virtual_desktops())
        if loop:
            pos = ((pos - 1) % total) + 1
        if pos < 0 or pos > total:
            raise ValueError(f"Invalid desktop number {pos}")

        return VirtualDesktop(pos)

    @handles(DesktopCommands.pan_right)
    async def _pan_right(self, r_command: TriggeredCommand) -> None:
        def do_pan_right():
            current_vd = self.current_vd
            next = self.get_desktop_at(current_vd.number + 1, loop=True)
            next.go()
            return Pan(current_vd, next).from_command(r_command)

        exec = r_command.execute(do_pan_right)
        self.set_value(exec)

    @handles(DesktopCommands.pan_left)
    async def _pan_left(self, r_command: TriggeredCommand) -> None:
        def do_pan_left():
            current_vd = self.current_vd
            next = self.get_desktop_at(current_vd.number - 1, loop=True)
            next.go()
            return Pan(current_vd, next).from_command(r_command)

        exec = r_command.execute(do_pan_left)
        self.set_value(exec)

    @handles(DesktopCommands.pan_to)
    async def _pan_to(self, to: int, r_command: TriggeredCommand) -> None:
        def do_pan_to():
            current_vd = self.current_vd
            target_vd = self.get_desktop_at(to)
            target_vd.go()
            return Pan(current_vd, target_vd).from_command(r_command)

        exec = r_command.execute(do_pan_to)
        self.set_value(exec)

    @handles(DesktopCommands.shove_to)
    async def _shove_to(self, to: int, r_command: TriggeredCommand) -> None:
        def do_shove_to():
            target_vd = self.get_desktop_at(to)
            infos, avs = get_related_windows(AppView.current())
            for av in avs:
                av.move(target_vd)
            return Shove(infos, self.current_vd, target_vd).from_command(r_command)

        exec = r_command.execute(do_shove_to)
        self.set_value(exec)

    @handles(DesktopCommands.shove_right)
    async def _shove_right(self, r_command: TriggeredCommand) -> None:
        def do_shove_right():
            current_vd = self.current_vd
            next = self.get_desktop_at(current_vd.number + 1, loop=True)
            infos, avs = get_related_windows(AppView.current())
            for current in avs:
                current.move(next)

            return Shove(infos, current_vd, next).from_command(r_command)

        exec = r_command.execute(do_shove_right)
        self.set_value(exec)

    @handles(DesktopCommands.shove_left)
    async def _shove_left(self, r_command: TriggeredCommand) -> None:
        def do_shove_left():
            current_vd = self.current_vd
            next = self.get_desktop_at(current_vd.number - 1, loop=True)
            infos, avs = get_related_windows(AppView.current())
            for current in avs:
                current.move(next)
            return Shove(infos, current_vd, next).from_command(r_command)

        exec = r_command.execute(do_shove_left)
        self.set_value(exec)

    @handles(DesktopCommands.drag_right)
    async def _drag_right(self, r_command: TriggeredCommand) -> None:
        def do_drag_right():
            current_vd = self.current_vd
            next = self.get_desktop_at(current_vd.number + 1, loop=True)

            infos, avs = get_related_windows(AppView.current())
            for current in avs:
                current.move(next)
            next.go()
            return Pan(current_vd, next).from_command(
                r_command, Shove(infos, current_vd, next)
            )

        exec = r_command.execute(do_drag_right)
        self.set_value(exec)

    @handles(DesktopCommands.no_caps)
    async def _no_caps(self, r_command: TriggeredCommand) -> None:
        if GetKeyState(VK_CAPITAL):
            keyboard.press_and_release("capslock")

    @handles(DesktopCommands.drag_left)
    async def _drag_left(self, r_command: TriggeredCommand) -> None:
        def do_drag_left():
            current_vd = self.current_vd
            next = self.get_desktop_at(current_vd.number - 1, loop=True)
            infos, avs = get_related_windows(AppView.current())
            for current in avs:
                current.move(next)
            next.go()
            return Pan(current_vd, next).from_command(
                r_command, Shove(infos, current_vd, next)
            )

        exec = r_command.execute(do_drag_left)
        self.set_value(exec)

    @handles(DesktopCommands.drag_to)
    async def _drag_to(self, to: int, r_command: TriggeredCommand) -> None:
        def do_drag_to():
            current_vd = self.current_vd
            target_vd = self.get_desktop_at(to)
            infos, avs = get_related_windows(AppView.current())
            for current in avs:
                current.move(target_vd)
            target_vd.go()
            return Shove(infos, current_vd, target_vd).from_command(
                r_command, Pan(current_vd, target_vd)
            )

        exec = r_command.execute(do_drag_to)
        self.set_value(exec)

    def __call__(self, command: TriggeredCommand) -> None:
        if self._current and command.timestamp - self._current.timestamp < 0.25:
            return
        with self._lock:
            match self._current:
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
            self._thread_pool.submit(self._exec, command)
