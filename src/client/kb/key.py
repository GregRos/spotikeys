from __future__ import annotations

from typing import TYPE_CHECKING

from keyboard import KeyboardEvent
import keyboard


if TYPE_CHECKING:
    from src.commanding import Command

from src.client.kb.labels import key_labels


class Key:
    def __init__(self, key_id: str):
        self.id = key_id

    @property
    def label(self):
        return key_labels.get(self.id, self.id)

    def match_event(self, e: KeyboardEvent):
        if (e.is_keypad) != ("num" in self.id):
            return False
        return e.name == self.hook_id

    @property
    def hook_id(self):
        match self.id:
            case "num enter":
                return "enter"
            case "num dot" | "num .":
                return "."
            case "num slash" | "num /":
                return "/"
            case "num star" | "num *" | "num multiply":
                return "*"
            case _:
                return self.id

    def __str__(self):
        return f"{self.label}  {self.id}"

    def lwin(self):
        return self.modified(Key("left windows"))

    def win(self):
        return self.modified(Key("windows"))

    @property
    def hotkey_id(self):
        return self.hook_id

    def modified(self, modifier: Key):
        return ModifiedKey(self, modifier)

    def bind_numpad(self, command: Command, alt: Command | None = None):
        from src.client.kb.bindings import NumpadBinding

        return NumpadBinding(self, command, alt)

    def bind_off(self):
        from src.client.kb.bindings import OffBinding

        return OffBinding(self)

    def bind_up_down(self, down: Command, up: Command):
        from src.client.kb.bindings import UpDownBinding

        return UpDownBinding(self, down, up)


class ModifiedKey:
    def __init__(self, base: Key, modifier: Key):
        self.base = base
        self.modifier = modifier

    def match_event(self, e: KeyboardEvent):
        return self.base.match_event(e) and keyboard.is_pressed(self.modifier.hook_id)

    @property
    def hook_id(self):
        return self.base.hook_id

    @property
    def hotkey_id(self):
        return f"{self.modifier.hook_id}+{self.base.hook_id}"

    @property
    def id(self):
        return f"{self.modifier.id} + {self.base.id}"

    @property
    def label(self):
        return f"{self.modifier.label} + {self.base.label}"

    def __str__(self):
        return f"{self.modifier} + {self.base}"

    def bind(
        self,
        command: Command,
        leftMouse: Command | None = None,
        rightMouse: Command | None = None,
    ):
        from src.client.kb.bindings import DownBinding

        return DownBinding(self, command, leftMouse, rightMouse)
