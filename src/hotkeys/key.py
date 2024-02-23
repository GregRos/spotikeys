from __future__ import annotations

from typing import Callable

from keyboard import KeyboardEvent

from commanding import Command
from hotkeys import Hotkey
from hotkeys.numpad_hotkey import NumpadHotkey
from src.hotkeys.labels import key_labels


class Key:
    def __init__(self, key_id: str):
        self.id = key_id

    @property
    def label(self):
        return key_labels.get(self.id, self.id)

    def __str__(self):
        return f"{self.label} ({self.id})"

    def modified(self, modifier: Key):
        return ModifiedKey(self, modifier)

    def bind_numpad(self, command: Command, alt: Command | None = None):
        return NumpadBinding(self, command, alt)

    def bind_off(self):
        return OffBinding(self)

    def bind_up_down(self, down: Command, up: Command):
        return UpDownBinding(self, down, up)

    def hotkey(
        self,
        on_down: Callable[[KeyboardEvent], None],
        on_up: Callable[[KeyboardEvent], None],
    ):
        return Hotkey(self, on_down, on_up)


class OffBinding:
    def __init__(self, key: Key):
        self.key = key
        pass


class UpDownBinding:
    def __init__(self, key: Key, down: Command, up: Command):
        self.key = key
        self.command_down = down
        self.command_up = up

    def __str__(self):
        return f"{self.key} -- {self.command_down}"

    def __repr__(self):
        return f"{self.key} -- {self.command_down}"


class NumpadBinding:
    def __init__(self, key: Key, command: Command, alt: Command | None = None):
        self.key = key
        self.command = command
        self.alt_command = alt

    def alt(self, command: Command):
        self.alt_command = command
        return self

    def __str__(self):
        return f"{self.key} -- {self.command}"

    def __repr__(self):
        return f"{self.key} -- {self.command}"


class ModifiedKey:
    def __init__(self, base: Key, modifier: Key):
        self.base = base
        self.modifier = modifier

    @property
    def label(self):
        return f"{self.modifier.label} + {self.base.label}"

    def __str__(self):
        return f"{self.modifier} + {self.base}"
