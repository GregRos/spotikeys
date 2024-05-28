from __future__ import annotations

from typing import Protocol, Callable, Any, TypeVar, Union


class CommandLike(Protocol):

    @property
    def code(self) -> str: ...

    @property
    def emoji(self) -> str: ...


class Command:
    code: str

    def __init__(self, command: str, emoji: str, title: str, group: str | None = None):
        self.code = command
        self.emoji = emoji
        self.title = title
        self.group = group

    def with_group(self, group: str):
        return Command(self.code, self.emoji, self.title, group)

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
        return f"{self.emoji} {self.title}"

    def __repr__(self):
        return f"Command('{self.emoji} {self.title}')"


class ParamterizedCommand[T](Command):
    __match_args__ = ("arg",)

    def __init__(
        self, command: str, emoji: str, title: str, arg: T, group: str | None = None
    ):
        super().__init__(command, emoji, title)
        self.arg = arg
        self.group = group

    def __str__(self):
        return f"{self.code}({self.arg})"

    def with_group(self, group: str):
        return ParamterizedCommand(self.code, self.emoji, self.title, self.arg, group)


def command(emoji: str, title: str):

    def decorator(func: Callable[[Any], None]):
        return Command(func.__name__, emoji, title)

    return decorator


class parameterized_command[Arg]:
    def __new__(
        cls,
        emoji: str | Callable[[Arg], str],
        title: str | Callable[[Arg], str],
        group: str | None = None,
    ):
        def decorator(func: Callable[[Any, Arg], Any]):
            return lambda arg: ParamterizedCommand(
                func.__name__,
                emoji.format(arg) if isinstance(emoji, str) else emoji(arg),
                title.format(arg) if isinstance(title, str) else title(arg),
                arg,
                group,
            )

        return decorator
