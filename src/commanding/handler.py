from abc import abstractmethod
from turtle import down
from typing import Callable, Any, Protocol

from src.commanding.commands import CommandLike, Command
from src.server.errors import LocalCommandError, NoHandlerError, BusyError


class CommandHandler[CommandType: CommandLike, ReturnType](Protocol):
    def __call__(self, command: CommandType) -> ReturnType: ...


class PropertyBasedCommandHandler[Command: Command, ReturnType](
    CommandHandler[Command, ReturnType]
):
    _current: Command | None = None

    def __init__(self, name: str):
        self._name = name

    def __call__(self, command: Command):
        handler = getattr(self, command.code, None)

        if not handler:
            raise NoHandlerError(command)

        if self._current:
            raise BusyError(self._current)

        self._current = command
        try:
            return_value = handler()
        finally:
            self._current = None
        return return_value
