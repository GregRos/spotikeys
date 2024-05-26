from threading import Lock
import threading
from time import sleep
from typing import Any, Callable, Self


class Updatable:
    _listeners: list[Callable[[Self], None]] = []
    _map: dict[str, Any] = {}

    def snapshot(self) -> "Self":
        return self.__class__(**self._map.copy())

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self._map == other._map

    def schedule(self, action: Callable[[Self], Any], delay: float) -> None:
        def do(x: Self):
            sleep(delay)
            if x == self:
                action(x)
            else:
                print("Snapshot changed, skipping action")

        thread = threading.Thread(target=do, args=(self.snapshot(),))
        thread.start()

    def __init__(self, **kwargs: Any):
        self._map = dict[str, Any](**kwargs)
        self._listeners = []

    def __getattr__(self, key: str) -> Any:
        if key in ["_map", "_listeners", "__annotations__"]:
            return super().__getattribute__(key)
        if key in self.__annotations__:
            return super().__getattribute__(key)
        if not key in self._map:
            return None
        return self._map[key]

    def __contains__(self, key: str) -> bool:
        return key in self._map

    def __iadd__(self, listener: Callable[[Self], Any]) -> Self:
        self._listeners.append(listener)
        return self

    def clone(self) -> Self:
        return self.__class__(**self._map)

    def _notify(self) -> None:
        for listener in self._listeners:
            listener(self)

    def _try_set(self, key: str, value: Any) -> None:
        if key in ["_map", "_listeners", "__annotations__"]:
            return super().__setattr__(key, value)
        if key in self.__annotations__:
            return super().__setattr__(key, value)

        self._map[key] = value

    def __call__(self, **kwargs: Any) -> Self:
        for k, v in kwargs.items():
            self._try_set(k, v)
        self._notify()
        return self

    def __setattr__(self, key: str, value: Any) -> None:
        self._try_set(key, value)
        self._notify()


class Ctx(Updatable):
    pass
