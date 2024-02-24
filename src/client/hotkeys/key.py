from __future__ import annotations

from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from commanding import Command

from src.hotkeys.labels import key_labels


class Key:
    def __init__(self, key_id: str):
        self.id = key_id

    @property
    def label(self):
        return key_labels.get(self.id, self.id)

    @property
    def hook_id(self):
        return (
            self.id.replace("num ", "")
            if self.id == "num enter" or self.id == "num ."
            else self.id
        )

    def __str__(self):
        return f"{self.label} ({self.id})"

    def modified(self, modifier: Key):
        return ModifiedKey(self, modifier)

    def bind_numpad(self, command: Command, alt: Command | None = None):
        from src.hotkeys.bindings import NumpadBinding

        return NumpadBinding(self, command, alt)

    def bind_off(self):
        from src.hotkeys.bindings import OffBinding

        return OffBinding(self)

    def bind_up_down(self, down: Command, up: Command):
        from src.hotkeys.bindings import UpDownBinding

        return UpDownBinding(self, down, up)


class ModifiedKey:
    def __init__(self, base: Key, modifier: Key):
        self.base = base
        self.modifier = modifier

    @property
    def label(self):
        return f"{self.modifier.label} + {self.base.label}"

    def __str__(self):
        return f"{self.modifier} + {self.base}"
