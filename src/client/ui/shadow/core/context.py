from threading import Lock
import threading
from typing import Any, Callable, Self


class Updatable:
    _listeners: list[Callable[[Self], None]]

    @classmethod
    def is_class_key(cls, key: str) -> bool:
        return key in cls.__dict__

    def snapshot(self) -> "Updatable":
        return Updatable(**self._map.copy())

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, self.__class__) and self._map == other._map

    def schedule(self, action: Callable[[Self], Any]) -> None:
        def do(x: Self):
            if x == self:
                action(x)
            else:
                print("Snapshot changed, skipping action")

        thread = threading.Thread(target=do)
        thread.start()

    def __init__(self, **kwargs: Any):
        self._map = dict[str, Any](kwargs=kwargs)
        self._listeners = []

    def __getattr__(self, key: str) -> Any:
        if __class__.is_class_key(key):
            return super().__getattribute__(key)
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
        if __class__.is_class_key(key):
            raise AttributeError(f"Cannot set attribute {key} on {__class__.__name__}")
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
