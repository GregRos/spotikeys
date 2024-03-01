from __future__ import annotations

from ast import Call
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


class ParamterizedCommand[T](Command):
    def __init__(self, command: str, label: str, arg: T):
        super().__init__(command, label)
        self.arg = arg

    def __str__(self):
        return f"{self.code}({self.arg})"

    @property
    def label(self):
        return f"{self.label} ⟵ {self.arg}"


def command(label: str):

    def decorator(func: Callable[[Any], None]):
        return Command(func.__name__, label)

    return decorator


def parameterized_command(label: str):

    def decorator[T](func: Callable[[Any, T], None]):
        return lambda arg: ParamterizedCommand(func.__name__, label, arg)

    return decorator
