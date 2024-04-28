from __future__ import annotations
from typing import Any, Callable


class Bindable[Value]:
    _bindings: dict[str, Callable[[Value], None]]
    _last_values: dict[str, Value]

    def _add_binding(self, key: str, action: Callable[[Value], None]):
        self._bindings[key] = action

    def _get(self, key: str):
        return self._last_values.get(key)

    def value(self, value: Value):
        for name, action in self._bindings.items():
            if self._last_values.get(name) != value:
                self._last_values[name] = value
                action(value)
        return self

    def _property_binding[
        Property
    ](self, binding: Callable[[Value], Property] | Property):
        if callable(binding):
            return binding
        return lambda x: binding

    def __call__(
        self,
        value: Value,
    ):
        for name, action in self._bindings.items():
            if self._last_values.get(name) != value:
                self._last_values[name] = value
                action(value)


class Binding[Value, Property]:
    _last_value: Property

    def __init__(
        self,
        binding: Callable[[Value], Property],
        *,
        initial: Property,
        tap: Callable[[Property, Any], None] | None = None,
    ) -> None:
        self._binding = binding
        self._last_value = initial
        self._tap = tap

    def default(self, value: Property):
        return Binding(self._binding, initial=value)

    def __call__(self, value: Value) -> Property:
        self._last_value = self._binding(value)
        if self._tap:
            self._tap(self._last_value, value)
        return self._last_value

    def map[X](self, f: Callable[[Property], X]) -> Binding[Value, X]:
        return Binding[Value, X](
            lambda x: f(self._binding(x)), initial=f(self._last_value)
        )


def const[Value](value: Value) -> Binding[Any, Value]:
    return Binding(lambda _: value, initial=value)
