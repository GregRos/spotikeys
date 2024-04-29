from typing import Any, Callable
from src.client.ui.binding.subscribable import Subscribable


class Default[X](Subscribable[X]):
    _source: Subscribable[X]

    def __init__(self, source: Subscribable[X], initial: X):
        self._source = source
        self._initial = initial

    def subscribe(self, action: Callable[[X], Any] | None = None):
        was_handled = False

        def handler(x: X):
            was_handled = True
            action(x) if action else None

        x = self._source.subscribe(handler)
        if not was_handled:
            action(self._initial) if action else None
        return x
