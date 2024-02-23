from datetime import datetime
from typing import Literal

from src.commands import code_labels
from src.hotkeys import Hotkey


class Command[Code: str]:
    code: Code

    def __init__(self, command: Code):
        self.code = command

    @property
    def cmd_label(self):
        return code_labels[self.code]

    def __str__(self):
        return f"{self.cmd_label}"

    def to_received(self, key: Hotkey):
        return ReceivedCommand(self, key)


class ReceivedCommand[Code: Literal](Command):
    def __init__(self, command: Command, hotkey: Hotkey):
        super().__init__(command.code)
        self.hotkey = hotkey
        self.received = datetime.now()

    def __str__(self):
        return f"{self.cmd_label} {self.hotkey.label}"
