from functools import reduce
from typing import Callable
from src.client.ui.binding.subscribable import Subscribable


class Reduce[In, Out](Subscribable[Out]):
    _last_value: Out

    def __init__(
        self, source: Subscribable[In], initial: Out, f: Callable[[Out, In], Out]
    ):
        self._source = source
        self._last_value = initial
        self._f = f

    def subscribe(self, action: Callable[[Out], None] | None = None):
        def handler(x: In):
            result = self._f(self._last_value, x)
            action(result) if action else None

        return self._source.subscribe(handler)
