from typing import Callable

import keyboard
from keyboard import KeyboardEvent

from src.commands.commands import Code
from src.commanding import Command
from src.client.kb import Key, ModifiedKey
from src.client.hotkeys.hotkey import Hotkey

num0_modifier = Key("num 0")


class NumpadHotkey(Hotkey):

    def __init__(
        self,
        key: Key,
        default_cb: Callable[[KeyboardEvent], None],
        alt_cb: Callable[[KeyboardEvent], None],
    ):
        super().__init__(key, self._on_down)
        self._default_cb = default_cb
        self._alt_cb = alt_cb

    def alt(self, command: Command):
        self.alt_command = command
        return self

    def _on_down(self, e: KeyboardEvent):
        if keyboard.is_pressed("num 0"):
            if self._alt_cb:
                self._alt_cb(e)
        else:
            self._default_cb(e)
