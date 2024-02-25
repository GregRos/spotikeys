from abc import abstractmethod
from typing import Callable, Any

from commanding import Command
from server import LocalCommandError, NoHandlerError, BusyError


class CommandHandler[Code: str]:
    _current: Command[Code] | None = None
    _handlers: dict[Code, Callable[[Command[Code]], Any]] = {}

    @abstractmethod
    def default_response(self):
        pass

    def register(self, command: Command):
        def decorator(callback: Callable[[Command[Code]], Any]):
            if command.code in self._handlers:
                raise ValueError(f"Handler for {command} already exists")

            self._handlers[command.code] = callback
            return callback

        return decorator

    def receive(self, command: Command[Code]):
        handler = self._handlers.get(command.code)
        if command.is_local:
            raise LocalCommandError(command)
        if not handler:
            raise NoHandlerError(command)

        if self._current:
            raise BusyError(self._current)

        self._current = command
        return_value = handler(command)
        self._current = None
        return return_value or self.default_response()
