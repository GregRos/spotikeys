from abc import abstractmethod
from typing import Callable, Any

from commanding import Command
from server import LocalCommandError, NoHandlerError, BusyError


class CommandHandler:
    _current: Command | None = None

    def __init__(self, command_set: str):
        self._command_set = command_set

    def __call__(self, command: Command):
        handler = getattr(self, command.code, None)
        if command.is_local:
            raise LocalCommandError(command)
        if not handler:
            raise NoHandlerError(command)

        if self._current:
            raise BusyError(self._current)

        self._current = command
        return_value = handler(command)
        self._current = None
        return return_value
