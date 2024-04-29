from typing import Any, Callable
from src.client.ui.framework.Disposable import Disposable
from src.client.ui.framework.subscribable import Subscribable


class ZippedValue(Subscribable[tuple[Any, ...]]):
    _last_value: list[Any]

    def __init__(self, sources: tuple[Subscribable[Any], ...]):
        self._last_value = [None] * len(sources)
        self._sources = sources

    def subscribe(self, action: Callable[[tuple[Any, ...]], Any] | None = None):
        def zip_handler(vs: tuple[Any, ...]):
            action(vs) if action else None  # type: ignore
            self._last_value = vs  # type: ignore

        def single_handler(i: int):
            def handler(x: Any):
                self._last_value[i] = x
                if all(self._last_value):
                    zip_handler(tuple(self._last_value))

            return handler

        combined = Disposable(lambda: None)
        for i, source in enumerate(self._sources):
            combined += source.subscribe(single_handler(i))

        return combined
