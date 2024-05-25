from logging import getLogger
from typing import Any, Awaitable, Callable

import keyboard
from referencing import Anchor


from src.kb.key_combination import KeyCombination
from src.kb.triggered_command import TriggeredCommand
from src.kb.compound_binding import CompoundBinding
from src.kb.key import Key
from src.commanding.commands import Command, CommandLike

logger = getLogger("keyboard")


def fix_padding_len(text: str):
    if "*️⃣️" in text:
        return 4
    elif "➗‍‍" in text:
        return 2
    elif "⏎" in text:
        return 1
    elif "\ufe0f" in text:
        return 3
    else:
        return 0


class Layout:
    _bindings: dict[Key, CompoundBinding]
    _registered: list[Any]

    def __init__(self, name: str, send: Callable[[TriggeredCommand], None]):
        self._bindings = {}
        self._registered = []
        self.name = name
        self._send = send

    def add_bindings(self, *bindings: CompoundBinding):
        for binding in bindings:
            self._bindings[binding.trigger] = binding

    def __str__(self):
        def binding_to_row(binding: CompoundBinding):
            default = binding.modifiers.get(KeyCombination(set()))
            no_default = [(k, v) for k, v in binding if not k.is_empty]
            return [
                f"{str(binding.trigger)} ➤",
                str(default),
                *[f"{k} ➜  {v}" for k, v in no_default],
            ]

        rows = [*map(binding_to_row, self._bindings.values())]
        cols_width = [
            max(len(row[i]) if i < len(row) else 0 for row in rows) + 2
            for i in range(max(map(len, rows)))
        ]

        return "\n".join(
            " | ".join(
                f"{row[i]:<{cols_width[i] + fix_padding_len(row[i])}}"
                for i in range(len(row))
            )
            for row in rows
        )

    def __enter__(self):
        logger.info(f"Entering layout {self.name} with {len(self._bindings)} hotkeys")
        logger.info("\n" + str(self))
        for binding in self._bindings.values():
            self._registered += [
                keyboard.hook_key(
                    binding.trigger.hook_id,
                    suppress=True,
                    callback=binding.handler(self._send),
                )
            ]
        return self

    def __exit__(self, *args):
        logger.info(f"Exiting layout {self.name}")
        for registration in self._registered:
            keyboard.unhook(registration)
