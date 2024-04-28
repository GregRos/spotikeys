from os import name
from typing import Any, Callable
from src.client.ui.framework.active_value import Disposable, Subscribable


class BindableProperty[Value]:
    _binding: Disposable

    def __init__(self, name: str, on_change: Callable[[Value], None]):
        self._name = name
        self._on_change = on_change

    def set(self, binding: Subscribable[Value]):
        if self._binding:
            self._binding.close()
        self._binding = binding.subscribe(self._on_change)


def bindable[Value](only_changed=False):
    def decorator[
        Self
    ](original: Callable[[Self, Value], Any]) -> Callable[
        [Self, Subscribable[Value] | Value], Self
    ]:
        name = original.__name__

        def wrapper(self: Self, source: Subscribable[Value] | Value) -> Self:
            if not isinstance(source, Subscribable):
                original(self, source)
                return self
            bindings = getattr(self, "bindings", None)
            if not bindings:
                bindings = {}
                setattr(self, "bindings", bindings)
            existing: Disposable | None = bindings.get(name)
            if existing:
                existing.close()
            x = source if not only_changed else source.only_changed()
            bindings[name] = x.subscribe(lambda x: original(self, x))
            return self

        return wrapper

    return decorator
