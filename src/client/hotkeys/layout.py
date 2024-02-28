from logging import getLogger
import logging
from typing import Callable

import keyboard

from src.client.kb.key import Key, ModifiedKey
from src.client.kb.bindings import (
    Binding,
    OffBinding,
    UpDownBinding,
    NumpadBinding,
)
from src.client.hotkeys.numpad_hotkey import NumpadHotkey
from src.commanding.commands import Command
from ..received_command import ReceivedCommand
from .hotkey import Hotkey

logger = getLogger("keyboard")


class Layout:
    _hotkeys: dict[Binding, Hotkey]

    def __init__(self, name: str, send: Callable[[ReceivedCommand], None]):
        self._hotkeys = {}
        self.name = name
        self._send = send

    def _binding_to_hotkey(self, binding: Binding):
        def send_command(command: Command | None):
            if command is None:
                return lambda e: None

            def send(e: keyboard.KeyboardEvent):
                if not self._send:
                    raise ValueError("No send function set")
                self._send(ReceivedCommand(command, binding.key))

            return send

        match binding:
            case OffBinding(key):
                return Hotkey(key, lambda e: None)
            case UpDownBinding(key, down, up):
                return Hotkey(key, send_command(down), send_command(up))
            case NumpadBinding(key, default, alt):
                return NumpadHotkey(key, send_command(default), send_command(alt))
            case _:
                raise ValueError(f"Binding type not supported: {binding}")

    def add_bindings(self, *bindings: Binding):
        for binding in bindings:
            self._hotkeys[binding] = self._binding_to_hotkey(binding)

    def __enter__(self):
        logger.info(f"Entering layout {self.name} with {len(self._hotkeys)} hotkeys")

        # rounded arrow:
        for binding, hotkey in self._hotkeys.items():
            logger.info(f"Registering {binding}")
            hotkey.__enter__()
        return self

    def __exit__(self, *args):
        logger.info(f"Exiting layout {self.name}")
        for hotkey in self._hotkeys.values():
            hotkey.__exit__()
