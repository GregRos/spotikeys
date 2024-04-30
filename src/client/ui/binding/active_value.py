from typing import (
    Annotated,
    Any,
    Callable,
    Protocol,
    TypeAlias,
    TypeVar,
    TypeVarTuple,
    TypedDict,
    Unpack,
    overload,
    runtime_checkable,
)

from src.client.ui.binding.closable import Closable
from src.client.ui.binding.subscribable import Subscribable


class ActiveValue[Value](Subscribable[Value]):
    current: Value | None
    _on_change: list[Callable[[Value], None]]
    _push_initial = False
    _name: str

    def __init__(
        self,
        name: str,
        initial: Value | None = None,
        scheduler: Callable[[Callable[[], Any]], Any] = lambda f: f(),
    ):
        self.current = initial
        self._push_initial = initial is not None
        self._name = name
        self._scheduler = scheduler
        self._on_change = []

    def bind(self, other: Subscribable[Value]):
        return other.subscribe(self.set)

    def set(self, value: Value):
        def action():
            for handler in self._on_change:
                handler(value)
            self.current = value

        return self._scheduler(action)

    def subscribe(self, action: Callable[[Value], Any] | None = None):
        action = action or (lambda x: None)

        def handler(value: Value):
            action(value)

        if self._push_initial and self.current is not None:
            action(self.current)
        self._on_change.append(handler)
        return Closable(lambda: self._on_change.remove(handler))
