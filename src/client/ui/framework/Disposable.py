from typing import Any, Callable


class Disposable:
    def __init__(self, action: Callable[[], Any]):
        self._action = action

    def close(self):
        self._action()

    def __add__(self, other: "Disposable") -> "Disposable":
        return Disposable(lambda: (self.close(), other.close()))
