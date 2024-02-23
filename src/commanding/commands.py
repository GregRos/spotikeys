from datetime import datetime
from typing import Literal

from src.commands import code_labels, Hotkey, key_labels


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
    def __init__(self, command: Command, key: Hotkey):
        super().__init__(command.code)
        self.key = key
        self.received = datetime.now()

    @property
    def key_label(self):
        def get_label(k):
            return key_labels[k.replace("num ", "")]

        keys = self.key if isinstance(self.key, tuple) else (self.key,)
        return "➿".join(get_label(k) for k in keys)

    def __str__(self):
        return f"{self.cmd_label} {self.key_label}"
