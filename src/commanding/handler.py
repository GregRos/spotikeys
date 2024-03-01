from abc import abstractmethod
from turtle import down
from typing import Awaitable, Callable, Any, Generic, Protocol, TypeVar

from src.commanding.commands import CommandLike, Command
from src.server.errors import LocalCommandError, NoHandlerError, BusyError

CommandType = TypeVar("CommandType", bound=CommandLike, contravariant=True)
ReturnType = TypeVar("ReturnType", covariant=True)


class AsyncCommandHandler(Protocol, Generic[CommandType, ReturnType]):
    def __call__(self, command: CommandType) -> Awaitable[ReturnType]: ...


class PropertyBasedCommandHandler(AsyncCommandHandler[CommandType, ReturnType]):
    _current: Command | None = None

    def __init__(self, name: str):
        self._name = name
