from __future__ import annotations

from typing import Protocol, Callable, Any, TypeVar, Union


class CommandLike(Protocol):

    @property
    def code(self) -> str: ...


class Command:
    code: str

    def __init__(self, command: str, label: str, describe: str | None = None):
        self.code = command
        self.label = label
        self.describe = describe

    def local(self, is_local: bool = True):
        return Command(self.code, self.label)

    def is_command(self, command: Command):
        return self.code == command.code

    def __eq__(self, other: object):
        if not isinstance(other, Command):
            return NotImplemented
        return self.code == other.code

    def __hash__(self):
        return hash(self.code)

    def __str__(self):
        return f"{self.code}"


class ParamterizedCommand[T](Command):
    __match_args__ = ("arg",)

    def __init__(self, command: str, label: str, arg: T):
        super().__init__(command, label)
        self.arg = arg
        self.label = f"{label}({arg})"

    def __str__(self):
        return f"{self.code}({self.arg})"


def command(label: str):

    def decorator(func: Callable[[Any], None]):
        return Command(func.__name__, label)

    return decorator


Returns = TypeVar("Returns")
Arg = TypeVar("Arg")


def parameterized_command(label: str):

    def decorator(
        func: Callable[[Any, Arg], Returns]
    ) -> Callable[[Arg], ParamterizedCommand[Arg]]:
        return lambda arg: ParamterizedCommand(func.__name__, label, arg)

    return decorator
