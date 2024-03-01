from __future__ import annotations

from src.commanding import Command
from src.client.kb.key import Key


class OffBinding:
    __match_args__ = ("key",)

    def __init__(self, key: Key):
        self.key = key
        pass

    def __str__(self) -> str:
        return f"{self.key.id} ➜  ∅"


class UpDownBinding:
    __match_args__ = ("key", "command_down", "command_up")

    def __init__(self, key: Key, down: Command, up: Command):
        self.key = key
        self.command_down = down
        self.command_up = up

    def __str__(self):
        return f"{self.key} ➜  {self.command_down}"

    def __repr__(self):
        return f"{self.key} ➜  {self.command_down}"


class NumpadBinding:
    __match_args__ = ("key", "command", "alt_command")

    def __init__(self, key: Key, command: Command, alt: Command | None = None):
        self.key = key
        self.command = command
        self.alt_command = alt

    def alt(self, command: Command):
        self.alt_command = command
        return self

    def __str__(self):
        return f"{self.key} ➜  {self.command} {self.alt_command}"


type Binding = OffBinding | UpDownBinding | NumpadBinding
