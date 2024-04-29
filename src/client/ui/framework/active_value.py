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

from src.client.ui.framework.Disposable import Disposable
from src.client.ui.framework.subscribable import Subscribable


class ActiveValue[Value](Subscribable[Value]):
    _last_value: Value | None
    _on_change: list[Callable[[Value], None]]
    _push_initial = False
    _name: str

    def __init__(
        self,
        name: str,
        initial: Value | None = None,
        scheduler: Callable[[Callable[[], Any]], Any] = lambda f: f(),
    ):
        self._last_value = initial
        self._push_initial = initial is not None
        self._name = name
        self._scheduler = scheduler
        self._on_change = []

    def set(self, value: Value):
        def action():
            for handler in self._on_change:
                handler(value)
            self._last_value = value

        return self._scheduler(action)

    def set_action(self, value: Value):
        return lambda: self.set(value)

    def subscribe(self, action: Callable[[Value], Any] | None = None):
        action = action or (lambda x: None)

        def handler(value: Value):
            action(value)

        if self._push_initial and self._last_value is not None:
            action(self._last_value)
        self._on_change.append(handler)
        return Disposable(lambda: self._on_change.remove(handler))
