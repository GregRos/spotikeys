from __future__ import annotations

from typing import Protocol, Callable, Any, TypeVar, Union


class CommandLike(Protocol):

    @property
    def code(self) -> str: ...

    @property
    def emoji(self) -> str: ...


class Command:
    code: str

    def __init__(self, command: str, emoji: str, title: str):
        self.code = command
        self.emoji = emoji
        self.title = title

    def __repr__(self):
        return f"{self.emoji} {self.title}"

    def is_command(self, command: Command | str):
        return (
            self.code == command.code
            if isinstance(command, Command)
            else self.code == command
        )

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

    def __init__(self, command: str, emoji: str, title: str, arg: T):
        super().__init__(command, emoji, title)
        self.arg = arg
        self.label = f"{emoji}({arg})"

    def __str__(self):
        return f"{self.code}({self.arg})"


def command(emoji: str, title: str):

    def decorator(func: Callable[[Any], None]):
        return Command(func.__name__, emoji, title)

    return decorator


Returns = TypeVar("Returns")
Arg = TypeVar("Arg")


def parameterized_command(
    title: str | Callable[[Arg], str], label: str | Callable[[Arg], str]
):

    def decorator(
        func: Callable[[Any, Arg], Returns]
    ) -> Callable[[Arg], ParamterizedCommand[Arg]]:
        return lambda arg: ParamterizedCommand(
            func.__name__,
            label if isinstance(label, str) else label(arg),
            title if isinstance(title, str) else title(arg),
            arg,
        )

    return decorator
