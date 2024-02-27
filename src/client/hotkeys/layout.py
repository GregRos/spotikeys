from typing import Callable

import keyboard

from .key import Key, ModifiedKey
from .bindings import Binding, OffBinding, UpDownBinding, NumpadBinding
from .numpad_hotkey import NumpadHotkey
from src.commanding.commands import Command
from src.client.received_command import ReceivedCommand
from .hotkey import Hotkey


class Layout:

    def __init__(self, name: str, send: Callable[[ReceivedCommand], None]):
        self._hotkeys = []
        self.name = name
        self._send = send

    def add_hotkey(self, hotkey: Hotkey):
        self._hotkeys.append(hotkey)

    def _binding_to_hotkey(self, binding: Binding):
        def send_command(command: Command | None):
            if command is None:
                return lambda e: None

            def send(e: keyboard.KeyboardEvent):
                print(f"Sending {command} for {e}")
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
        self._hotkeys += (self._binding_to_hotkey(binding) for binding in bindings)

    def __enter__(self):
        for hotkey in self._hotkeys:
            hotkey.__enter__()
        return self

    def __exit__(self, *args):
        for hotkey in self._hotkeys:
            hotkey.__exit__()
