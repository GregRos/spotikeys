from __future__ import annotations

from datetime import datetime

from src.client.hotkeys.key import Key, ModifiedKey
from src.commanding import Command


class ReceivedCommand[Code: str]:
    def __init__(self, command: Command, key: Key | ModifiedKey):
        self.command = command
        self.key = key
        self.received = datetime.now()

    def __str__(self):
        return f"{self.key.label} ➜ {self.command}"
