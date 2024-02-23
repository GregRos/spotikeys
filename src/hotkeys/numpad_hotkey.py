from typing import Callable

import keyboard
from keyboard import KeyboardEvent

from src.commanding import Command, ReceivedCommand
from src.hotkeys import Hotkey


class NumpadHotkey(Hotkey):
    def __init__(
        self,
        send: Callable[[ReceivedCommand], None],
        key: str,
        default_command: Command,
        alt_command: Command | None = None,
    ):
        self._send = send
        super().__init__(key, self._on_down)
        self.default_command = default_command
        self.alt_command = alt_command

    def _on_down(self, e: KeyboardEvent):
        if keyboard.is_pressed("num 0"):
            if self.alt_command:
                self._send(self.alt_command.to_received(self.key))
        else:
            self._send(self.default_command.to_received(self.key))
