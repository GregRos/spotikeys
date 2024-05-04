from threading import Lock
from typing import Any, Callable


class State:
    def __init__(self, on_change: Callable[["State"], None]):
        self.__on_change = on_change
        self.__map = dict[str, Any]()

    def __getattr__(self, key: str) -> Any:
        return self.__map[key]

    def __contains__(self, key: str) -> bool:
        return key in self.__map

    def get(self, key: str, /, default: Any = None) -> Any:
        return self.__map.get(key, default)

    def __call__(self, **kwargs: Any) -> None:
        for k, v in kwargs.items():
            setattr(self, k, v)
        self.__on_change(self)

    def __setattr__(self, key: str, value: Any) -> None:
        self.__map[key] = value
        self.__on_change(self)
