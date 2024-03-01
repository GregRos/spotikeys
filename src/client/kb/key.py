from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from src.commanding import Command

from src.client.kb.labels import key_labels


class Key:
    def __init__(self, key_id: str):
        self.id = key_id

    @property
    def label(self):
        return key_labels.get(self.id, self.id)

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

    @property
    def id(self):
        return f"{self.modifier.id} + {self.base.id}"

    @property
    def label(self):
        return f"{self.modifier.label} + {self.base.label}"

    def __str__(self):
        return f"{self.modifier} + {self.base}"
