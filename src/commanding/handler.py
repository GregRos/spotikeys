from functools import partial
from typing import Any, Awaitable, Callable, Generic, Protocol, TypeVar
from src.commanding.commands import CommandLike, Command, ParamterizedCommand

CommandType = TypeVar("CommandType", bound=CommandLike)
ReturnType = TypeVar("ReturnType")


class AsyncCommandHandler(Generic[CommandType, ReturnType]):
    _mapping: dict[str, Callable[[CommandType], ReturnType]]

    def get_handler(
        self, command: CommandType
    ) -> Callable[[CommandType], ReturnType] | None:
        local_handler = self._mapping.get(command.code, None)
        return local_handler

    def __init__(self) -> None:
        self._mapping = {}
        for name in dir(self):
            handler = self.__class__.__dict__.get(name)
            if not handler:
                continue
            if not hasattr(handler, "handles"):
                continue
            for code in handler.handles:
                if code in self._mapping:
                    raise ValueError(f"Duplicate handler for {code}")
                self._mapping[code] = partial(handler, self)

    def __call__(self, command: CommandType) -> ReturnType: ...


class PropertyBasedCommandHandler(AsyncCommandHandler[CommandType, ReturnType]):
    _current: Command | None = None

    def __init__(self, name: str):
        super().__init__()
        self._name = name


def handles(*commands: Command | Callable[[Any], ParamterizedCommand]) -> Any:
    def decorator(handler: Any):

        setattr(
            handler,
            "handles",
            [c.code if isinstance(c, Command) else c(0).code for c in commands],
        )
        return handler

    return decorator
