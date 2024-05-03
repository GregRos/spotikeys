from typing import Any, Callable, Protocol, overload, runtime_checkable

from src.client.ui.binding.closable import Closable


class Subscribable[Value]:
    def __init__(self) -> None:
        super().__init__()

    def subscribe(self, action: Callable[[Value], Any] | None = None) -> Closable: ...

    def map[X](self, f: Callable[[Value], X]) -> "Subscribable[X]":
        from src.client.ui.binding.map import MappedValue

        return MappedValue[Value, X](self, f)

    def filter(self, f: Callable[[Value], bool]) -> "Subscribable[Value]":
        from src.client.ui.binding.filter import FilteredValue

        return FilteredValue(self, f)

    def of_type[X](self, t: type[X]) -> "Subscribable[X]":
        from src.client.ui.binding.filter import FilteredValue

        return self.filter(lambda x: isinstance(x, t))  # type: ignore

    def tap(self, f: Callable[[Value], Any]) -> "Subscribable[Value]":
        return self.map(lambda x: (f(x), x)[1])

    def tap_after(self, f: Callable[[Value], Any]) -> "Subscribable[Value]":
        from src.client.ui.binding.tap_after import TapAfter

        return TapAfter(self, f)

    def only_changed(self) -> "Subscribable[Value]":
        from src.client.ui.binding.only_changed import OnlyChanged

        return OnlyChanged(self)

    def reduce[X](self, initial: X, f: Callable[[X, Value], X]) -> "Subscribable[X]":
        from src.client.ui.binding.reduce import Reduce

        return Reduce[Value, X](self, initial, f)

    def default(self, initial: Value) -> "Subscribable[Value]":
        from src.client.ui.binding.default import Default

        return Default(self, initial)

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
        from src.client.ui.binding.zip import ZippedValue

        return ZippedValue((self, *args))