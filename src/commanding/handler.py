from typing import Awaitable, Generic, Protocol, TypeVar

from src.commanding.commands import CommandLike, Command

CommandType = TypeVar("CommandType", bound=CommandLike, contravariant=True)
ReturnType = TypeVar("ReturnType", covariant=True)


class AsyncCommandHandler(Protocol, Generic[CommandType, ReturnType]):
    def __call__(self, command: CommandType) -> Awaitable[ReturnType]: ...


class PropertyBasedCommandHandler(AsyncCommandHandler[CommandType, ReturnType]):
    _current: Command | None = None

    def __init__(self, name: str):
        self._name = name
