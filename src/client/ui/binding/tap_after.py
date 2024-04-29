from typing import Any, Callable

from src.client.ui.binding.subscribable import Subscribable


class TapAfter[X](Subscribable[X]):
    _last_value: X | None = None

    def __init__(self, source: Subscribable[X], f: Callable[[X], Any]):
        self._source = source
        self._f = f

    def subscribe(self, action: Callable[[X], Any] | None = None):
        def handler(x: X):
            action(x) if action else None
            self._last_value = x
            self._f(x)

        return self._source.subscribe(handler)
