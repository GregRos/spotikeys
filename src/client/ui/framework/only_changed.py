from typing import Any, Callable

from src.client.ui.framework.subscribable import Subscribable


class OnlyChanged[Value](Subscribable[Value]):
    _last_value: Value | None = None

    def __init__(self, source: Subscribable[Value]):
        self._source = source

    def subscribe(self, action: Callable[[Value], Any] | None = None):
        def handle(x: Value):
            if self._last_value != x:
                action(x) if action else None
                self._last_value = x

        return self._source.subscribe(handle)
