from datetime import datetime
from typing import Literal

from src.hotkeys.key import Key, ModifiedKey


class Command[Code: str]:
    code: Code

    def __init__(self, command: Code, label: str):
        self.code = command
        self.label = label

    def __str__(self):
        return f"{self.label} ({self.code})"

    def to_received(self, key: Key | ModifiedKey):
        return ReceivedCommand[Code](self, key)


class ReceivedCommand[Code: str](Command):
    def __init__(self, command: Command, key: Key | ModifiedKey):
        super().__init__(command.code, command.label)
        self.key = key
        self.received = datetime.now()

    def __str__(self):
        return f"{self.received}: {self.key} -- {self.label} ({self.code})"
