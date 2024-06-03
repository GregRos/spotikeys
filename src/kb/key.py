from __future__ import annotations

from functools import total_ordering
from time import sleep
from typing import TYPE_CHECKING, Literal, Optional, overload
from keyboard import KeyboardEvent
import keyboard
from win32api import GetAsyncKeyState
from src.commanding.commands import CommandLike


if TYPE_CHECKING:
    from src.commanding import Command


from src.kb.labels import key_labels


@total_ordering
class Key:
    def __init__(self, key_id: str, type: Literal["kb", "mouse", None] = None) -> None:
        if type:
            if ":" in key_id:
                raise ValueError(
                    f"Cannot specify type and fully qualified key id {key_id}"
                )
            self.id = key_id
            self.type = type
        elif ":" in key_id:
            self.type, self.id = key_id.split(":")
        else:
            self.id = key_id
            self.type = "kb"

    @property
    def specificity(self):
        return 1

    @property
    def id2(self):
        if self.type == "kb":
            return self.id
        return f"{self.type}:{self.id}"

    @property
    def label(self):
        return key_labels.get(self.id2) or self.id

    def match_event(self, e: KeyboardEvent):
        if (e.is_keypad) != ("num" in self.id):
            return False
        return True

    def __add__(self, other: Key):
        from src.kb.key_combination import KeyCombination

        return KeyCombination({self, other})

    def __lt__(self, other: Key) -> bool:
        return self.id < other.id

    @property
    def fqn(self):
        return f"{self.type}:{self.id}"

    def is_pressed(self):
        if self.type == "mouse":
            pr = GetAsyncKeyState(int(self.id)) & 0x8000
            return pr
        else:
            return keyboard.is_pressed(self.hook_id)

    @property
    def hook_id(self):
        match self.type, self.id:
            case "kb", "num enter":
                return "enter"
            case "kb", "num dot" | "num .":
                return "."
            case "kb", "num star" | "num *" | "num multiply":
                return "*"
            case "kb", "num plus" | "num +":
                return "+"
            case "kb", "num minus" | "num -":
                return "-"
            case "kb", "num slash" | "num /":
                return "/"
            case "mouse", "1":
                return "left"
            case "mouse", "2":
                return "right"
            case "mouse", "3":
                return "middlemouse"
            case "mouse", "4":
                return "x"
            case "mouse", "5":
                return "x2"
            case _:
                return self.id

    def __str__(self):
        return f"[{self.label}]"

    def __repr__(self):
        return f"Key({self.label})"

    @property
    def hotkey_id(self):
        return self.hook_id

    @property
    def bind(self):
        from src.kb.compound_binding import CompoundBinding

        return CompoundBinding(self)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Key):
            return False
        return self.id == value.id

    def __hash__(self) -> int:
        return hash(self.id)
