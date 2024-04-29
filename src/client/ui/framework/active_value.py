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


class Disposable:
    def __init__(self, action: Callable[[], Any]):
        self._action = action

    def close(self):
        self._action()

    def __add__(self, other: "Disposable") -> "Disposable":
        return Disposable(lambda: (self.close(), other.close()))


@runtime_checkable
class Subscribable[Value](Protocol):
    def subscribe(self, action: Callable[[Value], Any] | None = None) -> Disposable: ...

    def map[X](self, f: Callable[[Value], X]) -> "Subscribable[X]":
        return MappedValue[Value, X](self, f)

    def filter(self, f: Callable[[Value], bool]) -> "Subscribable[Value]":
        return FilteredValue(self, f)

    def of_type[X](self, t: type[X]) -> "Subscribable[X]":
        return self.filter(lambda x: isinstance(x, t))  # type: ignore

    def tap(self, f: Callable[[Value], Any]) -> "Subscribable[Value]":
        return self.map(lambda x: (f(x), x)[1])

    def tap_after(self, f: Callable[[Value], Any]) -> "Subscribable[Value]":
        return TapAfter(self, f)

    def only_changed(self) -> "Subscribable[Value]":
        return OnlyChanged(self)

    def map_to[X](self, value: X) -> "Subscribable[X]":
        return self.map(lambda _: value)

    @overload
    def zip[A](self, a: "Subscribable[A]", /) -> "Subscribable[tuple[Value, A]]": ...

    @overload
    def zip[
        A, B
    ](
        self, a: "Subscribable[A]", b: "Subscribable[B]", /
    ) -> "Subscribable[tuple[Value, A, B]]": ...

    @overload
    def zip[
        A, B, C
    ](
        self, a: "Subscribable[A]", b: "Subscribable[B]", c: "Subscribable[C]", /
    ) -> "Subscribable[tuple[Value, A, B, C]]": ...

    @overload
    def zip[
        A, B, C, D
    ](
        self,
        a: "Subscribable[A]",
        b: "Subscribable[B]",
        c: "Subscribable[C]",
        d: "Subscribable[D]",
        /,
    ) -> "Subscribable[tuple[Value, A, B, C, D]]": ...

    @overload
    def zip[
        A, B, C, D, E
    ](
        self,
        a: "Subscribable[A]",
        b: "Subscribable[B]",
        c: "Subscribable[C]",
        d: "Subscribable[D]",
        e: "Subscribable[E]",
        /,
    ) -> "Subscribable[tuple[Value, A, B, C, D, E]]": ...

    def zip(self, *args: "Subscribable[Any]") -> "Subscribable[Any]":
        return ZippedValue((self, *args))


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


class FilteredValue[Value](Subscribable[Value]):
    _last_value: Value | None = None

    def __init__(self, source: Subscribable[Value], _filter: Callable[[Value], bool]):
        self._source = source
        self._filter = _filter

    def subscribe(self, action: Callable[[Value], Any] | None = None):
        def handle(x: Value):
            if self._filter(x):
                action(x) if action else None
                self._last_value = x

        return self._source.subscribe(handle)


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


class TapAfter[X](Subscribable[X]):
    _last_value: X | None = None

    def __init__(self, source: Subscribable[X], f: Callable[[X], Any]):
        self._source = source
        self._f = f

    def subscribe(self, action: Callable[[X], Any] | None = None):
        def handler(x: X):
            action(x) if action else None
            self._last_value = x
            self._f(x)

        return self._source.subscribe(handler)


class OnlyChanged[Value](Subscribable[Value]):
    _last_value: Value | None = None

    def __init__(self, source: Subscribable[Value]):
        self._source = source

    def subscribe(self, action: Callable[[Value], Any] | None = None):
        def handle(x: Value):
            if self._last_value != x:
                action(x) if action else None
                self._last_value = x

        return self._source.subscribe(handle)


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
