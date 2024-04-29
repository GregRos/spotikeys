from typing import Any, Callable


class Closable:
    def __init__(self, action: Callable[[], Any]):
        self._action = action

    def close(self):
        self._action()

    def __add__(self, other: "Closable") -> "Closable":
        return Closable(lambda: (self.close(), other.close()))
