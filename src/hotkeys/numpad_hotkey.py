from typing import Callable

import keyboard
from keyboard import KeyboardEvent

from src.commanding import Command, ReceivedCommand
from src.hotkeys import Hotkey, Key, ModifiedKey

num0_modifier = Key("num 0")


class NumpadHotkey(Hotkey):
    def __init__(
        self,
        send: Callable[[ReceivedCommand], None],
        key: Key,
        default_command: Command,
        alt_command: Command | None = None,
    ):
        super().__init__(key, self._on_down)
        self._send = send

        self.default_command = default_command
        self.alt_command = alt_command

    def _on_down(self, e: KeyboardEvent):
        if keyboard.is_pressed("num 0"):
            if self.alt_command:
                self._send(self.alt_command.to_received(self.key))
        else:
            self._send(
                self.default_command.to_received(self.key.modifier(num0_modifier))
            )
