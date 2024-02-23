from typing import Callable

import keyboard
from keyboard import KeyboardEvent

from commands.commands import Code
from src.commanding import Command, ReceivedCommand
from src.hotkeys import Hotkey, Key, ModifiedKey

num0_modifier = Key("num 0")


class NumpadHotkey(Hotkey):

    def __init__(
        self,
        key: Key,
        default_command: Command,
        alt_command: Command | None = None,
    ):
        super().__init__(key, self._on_down)
        self._send = send

        self.default_command = default_command
        self.alt_command = alt_command

    def alt(self, command: Command):
        self.alt_command = command
        return self

    def _on_down(self, e: KeyboardEvent):
        if keyboard.is_pressed("num 0"):
            if self.alt_command:
                self._send(
                    self.alt_command.to_received(self.key.modified(num0_modifier))
                )
        else:
            self._send(self.default_command.to_received(self.key))
