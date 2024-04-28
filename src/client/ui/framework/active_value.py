from typing import Callable, Protocol


class ActiveValue[Value]:
    _last_value: Value
    _on_change: list[Callable[[Value], None]]
    _name: str

    def __init__(self, name: str, initial: Value):
        self._last_value = initial
        self._name = name

    def set(self, value: Value):
        self._last_value = value
        for action in self._on_change:
            action(value)
        return self

    def map[X](self, f: Callable[[Value], X]) -> "MappedValue[Value, X]":
        return MappedValue(self, f)

    def subscribe(self, action: Callable[[Value], None]):
        owner = self

        def handler(value: Value):
            action(value)

        return Disposable(lambda: self._on_change.remove(handler))


class Disposable:
    def __init__(self, action: Callable[[], None]):
        self._action = action

    def dispose(self):
        self._action()


class MappedValue[In, Out]:
    _name: str

    def __init__(self, source: ActiveValue[In], _mapping: Callable[[In], Out]):
        self._source = source
        self._mapping = _mapping

    def subscribe(self, action: Callable[[Out], None]):
        return self._source.subscribe(lambda x: action(self._mapping(x)))

    def map[X](self, f: Callable[[Out], X]) -> "MappedValue[In, X]":
        return MappedValue(self._source, lambda x: f(self._mapping(x)))


class Subscribable[Value](Protocol):
    def subscribe(self, action: Callable[[Value], None]) -> Disposable: ...
