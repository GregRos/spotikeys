from datetime import datetime

from src.commanding import Command
from src.commanding.commands import CommandLike
from src.client.kb.key import Key, ModifiedKey


class ReceivedCommand(CommandLike):
    def __init__(self, command: Command, key: Key | ModifiedKey):
        self.command = command
        self.key = key
        self.received = datetime.now()

    def __str__(self):
        return f"{self.key.label} ➜ {self.command}"

    @property
    def code(self):
        return self.command.code

    @property
    def label(self):
        return self.command.label
