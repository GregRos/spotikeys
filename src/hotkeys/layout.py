from typing import Callable

import keyboard

from hotkeys import Key, ModifiedKey
from hotkeys.numpad_hotkey import NumpadHotkey
from src.commanding.commands import Command, ReceivedCommand
from src.hotkeys import Hotkey


class Layout:
    def __init__(self, name: str, send: Callable[[ReceivedCommand], None]):
        self._hotkeys = []
        self.name = name
        self._send = send

    def add(self, *hotkey: Hotkey):
        self._hotkeys.append(hotkey)
        return self

    def send(self, key: Key | ModifiedKey, command: Command):
        self._send(command.to_received(key))

    def __enter__(self):
        for hotkey in self._hotkeys:
            hotkey.__enter__()
        return self

    def __exit__(self, *args):
        for hotkey in self._hotkeys:
            hotkey.__exit__()
