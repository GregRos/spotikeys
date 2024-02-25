from __future__ import annotations

from typing import Protocol, Callable, Any


class Command:
    code: str

    def __init__(self, command: str, label: str, is_local: bool = False):
        self.code = command
        self.label = label
        self.is_local = is_local

    def local(self, is_local: bool = True):
        return Command(self.code, self.label, is_local)

    def is_command(self, command: Command):
        return self.code == command.code

    def __eq__(self, other: Command):
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)

    def __str__(self):
        return f"{self.label} ({self.code})"


def command(label: str):

    def decorator(func: Callable[[Any], None]):
        return Command(func.__name__, label)  # type: ignore

    return decorator
