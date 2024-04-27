from asyncio import AbstractEventLoop, new_event_loop
import comtypes
from logging import getLogger
import os
import threading
from typing import Any, Awaitable

from flask import current_app
import win32com
from src.client.kb.triggered_command import TriggeredCommand
from src.commanding.commands import Command, ParamterizedCommand
from src.commanding.handler import AsyncCommandHandler, handles
from src.commands.desktop_commands import DesktopCommands
from pyvda import AppView, VirtualDesktop, get_virtual_desktops

logger = getLogger("vda_client")


class VdaClient(AsyncCommandHandler[TriggeredCommand, None]):
    _loop: AbstractEventLoop

    def __init__(self, loop: AbstractEventLoop) -> None:
        super().__init__()
        self._current = None
        self._loop = loop
        self._lock = threading.Lock()

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

    @handles(DesktopCommands.move_next)
    def _move_next(self) -> None:
        current_vd = self.current_vd
        next = self.get_desktop_at(current_vd.number + 1, loop=True)
        next.go()

    @handles(DesktopCommands.move_prev)
    async def _move_prev(self) -> None:
        current_vd = self.current_vd
        next = self.get_desktop_at(current_vd.number - 1, loop=True)
        next.go()

    @handles(DesktopCommands.move_to)
    async def _move_to(self, to: int) -> None:
        target_vd = self.get_desktop_at(to)
        target_vd.go()

    @handles(DesktopCommands.fg_move_to_follow)
    async def _fg_move_to_follow(self, to: int) -> None:
        target_vd = self.get_desktop_at(to)
        AppView.current().move(target_vd)
        target_vd.go()

    @handles(DesktopCommands.fg_move_to)
    async def _fg_move_to(self, to: int) -> None:
        target_vd = self.get_desktop_at(to)
        AppView.current().move(target_vd)

    @handles(DesktopCommands.fg_move_next)
    async def _fg_move_next(self) -> None:
        current_vd = self.current_vd
        next = self.get_desktop_at(current_vd.number + 1, loop=True)
        AppView.current().move(next)

    @handles(DesktopCommands.fg_move_prev)
    async def _fg_move_prev(self) -> None:
        current_vd = self.current_vd
        next = self.get_desktop_at(current_vd.number - 1, loop=True)
        AppView.current().move(next)

    @handles(DesktopCommands.fg_move_next_follow)
    async def _fg_move_next_follow(self) -> None:
        current_vd = self.current_vd
        next = self.get_desktop_at(current_vd.number + 1, loop=True)
        AppView.current().move(next)
        next.go()

    @handles(DesktopCommands.fg_move_prev_follow)
    async def _fg_move_prev_follow(self) -> None:
        current_vd = self.current_vd
        next = self.get_desktop_at(current_vd.number - 1, loop=True)
        AppView.current().move(next)
        next.go()

    def _exec(self, command: TriggeredCommand) -> None:
        loop = self._loop
        try:
            handler: Any = self.get_handler(command)
            if handler:
                if isinstance(command.command, ParamterizedCommand):
                    handler = handler(command.command.arg)
                else:
                    handler = handler()
                loop.run_until_complete(handler)

        except RuntimeError as e:
            if "Event loop stopped before Future completed" in str(e):
                logger.warn(f"Event loop stopped before {command} completed.")
                loop.close()
                return
            raise
        except comtypes.COMError as e:
            logger.error(f"COM error: {e}")
        else:
            self._current = None

    def busy(self, command: TriggeredCommand) -> None:
        pass

    def __call__(self, command: TriggeredCommand) -> None:
        with self._lock:
            if self._current:
                return self.busy(command)
            self._current = command
        threading.Thread(target=self._exec, args=(command,)).start()
