from os import name
from typing import Any, Callable
from src.client.ui.binding.closable import Closable
from src.client.ui.binding.active_value import ActiveValue, Subscribable


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
            existing: Closable | None = bindings.get(name)
            if existing:
                existing.close()
            x = source if not only_changed else source.only_changed()
            bindings[name] = x.subscribe(lambda x: original(self, x))
            return self

        return wrapper

    return decorator
