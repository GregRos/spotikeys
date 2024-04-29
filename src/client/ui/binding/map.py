from typing import Any, Callable

from src.client.ui.binding.subscribable import Subscribable


class MappedValue[In, Out](Subscribable[Out]):
    _last_value: Out | None = None

    def __init__(self, source: Subscribable[In], _mapping: Callable[[In], Out]):
        self._source = source
        self._mapping = _mapping

    def subscribe(self, action: Callable[[Out], Any] | None = None):
        def handler(x: In):
            v = self._mapping(x)
            action(v) if action else None

        return self._source.subscribe(handler)
