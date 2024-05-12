from collections.abc import Mapping
from copy import copy
from typing import Any, Callable, Literal, cast, overload

from pydantic import Field
from pydantic.dataclasses import dataclass
from src.client.ui.shadow.core.props.operators import (
    SAME,
    Computable,
    Diffable,
    diff,
)


DiffMode = Literal["simple", "recursive", "never"]

@dataclass(kw_only=True)
class PropDef[X]:
    diff_mode: DiffMode = Field(default="recursive")
    kind: str = Field(default=None)
    alias: str = Field(default=None)
    default: X = Field(default=None)
    converter: Callable[[X], Any] = Field(default=None)
    value_type: type[X] = Field(default=None)

    def set(self, **kwargs: Any) -> "PropDef[X]":
        return copy(self, **kwargs)

    def transform(self, key: str, value: Any) -> tuple[str, Any]:
        return (self.alias or key, self.converter(value) if self.converter else value)

    def __bool__(self) -> bool:
        return False

    def wrap[Y](self, value: Y) -> "PropValue[Y]":
        return PropValue[Y](value, cast(PropDef[Y], self))

    def merge(self, other: "PropDef[X]") -> "PropDef[X]":
        return self.set(**{k: v for k, v in other.__dict__.items() if v is not None})


class JustValue[X]:
    __match_args__ = ("value",)

    def __init__(self, value: X):
        self.value = value


@dataclass(kw_only=True)
class PropValue[X](Computable, Diffable, JustValue[X]):
    __match_args__ = ("value", "prop")
    __slots__ = ("_cached", "value")
    _cached: tuple[str, X] | None = Field(default=None)

    def __init__(self, value: X, prop: PropDef[X]):
        JustValue.__init__(self, value)
        self.prop = prop
        self._cached = None

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, PropValue)
            and self.value == other.value
            and self.prop == other.prop
        )

    def delta_from(self, older: "PropValue[X]", /) -> Any:
        match self.prop.diff_mode:
            case "eq":
                return self.value if self.value == older.value else SAME
            case "full":
                return self.prop.wrap(diff(self.value, older.value))
            case "never":
                return self.value

    def compute(self, key: str) -> tuple[str, X]:
        if self._cached:
            return self._cached
        self._cached = self.prop.transform(key, self.value)
        return self._cached

    def __pos__(self) -> X:
        return self.compute("")[1]


type SomeProp[X] = PropValue[X] | PropDef[X] | JustValue[X]


@overload
def norm_prop[X](a: PropDef[X] | None, b: PropDef[X], /) -> PropDef[X]: ...
@overload
def norm_prop[X](a: PropValue[X], b: PropDef[X], /) -> PropValue[X]: ...
@overload
def norm_prop[X](a: PropDef[X], b: PropValue[X], /) -> PropValue[X]: ...
@overload
def norm_prop[
    X
](maybe_a: SomeProp[X] | None, maybe_b: SomeProp[X] | None, /) -> SomeProp[X]: ...
def norm_prop[
    X
](maybe_a: SomeProp[X] | None, maybe_b: SomeProp[X] | None, /) -> SomeProp[X]:
    match maybe_a, maybe_b:
        case None, None:
            assert False, "Expected a value"
        case None, prop if prop is not None:
            return prop
        case prop, None if prop is not None:
            return prop
        case (PropDef() as prop) | PropValue(_, prop), PropValue() as oth:
            return prop.merge(oth.prop).wrap(oth.value)
        case JustValue(), JustValue() as oth:
            return oth
        case JustValue(value), PropDef() as prop:
            return PropValue(value, prop)
        case (PropDef() as prop) | PropValue(_, prop), JustValue(value):
            return PropValue(value=value, prop=prop)
        case _:
            assert False, f"Unexpected combination {maybe_a} and {maybe_b}"


def norm_props(
    dict_a: Mapping[str, PropValue | PropDef | JustValue] | None = None,
    dict_b: Mapping[str, PropValue | PropDef | JustValue] | None = None,
) -> dict[str, PropValue | PropDef | JustValue]:
    dict_a = dict_a or {}
    dict_b = dict_b or {}
    all_props = {
        k: norm_prop(dict_a.get(k), dict_b.get(k))
        for k in dict_a.keys() | dict_b.keys()
    }
    return all_props
