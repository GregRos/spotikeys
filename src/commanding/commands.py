from __future__ import annotations

from typing import Protocol, Callable, Any


class CommandLike(Protocol):
    code: str
    label: str


class Command(CommandLike):
    code: str

    def __init__(self, command: str, label: str):
        self.code = command
        self.label = label

    def local(self, is_local: bool = True):
        return Command(self.code, self.label)

    def is_command(self, command: Command):
        return self.code == command.code

    def __eq__(self, other: Command):
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)

    def __str__(self):
        return f"{self.code}"


def command(label: str):

    def decorator(func: Callable[[Any], None]):
        return Command(func.__name__, label)  # type: ignore

    return decorator
