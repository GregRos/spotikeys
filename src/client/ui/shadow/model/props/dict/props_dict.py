from collections.abc import Mapping
from copy import copy
from dataclasses import field
from itertools import groupby
from types import SimpleNamespace
from typing import (
    Any,
    Callable,
    Concatenate,
    Iterable,
    Iterator,
    Literal,
    NotRequired,
    Optional,
    Protocol,
    Self,
    TypedDict,
    Unpack,
    cast,
    get_type_hints,
    overload,
    override,
    runtime_checkable,
)

from src.client.ui.shadow.model.props.from_type.read_annotations import (
    get_sections,
)
from src.client.ui.shadow.model.props.single.prop_def import PropDef
from src.client.ui.shadow.model.props.single.prop_value import PropValue
from src.client.ui.shadow.model.props.operators import (
    SAME,
    Computable,
    Diffable,
    diff,
)

from src.client.ui.values.geometry import Geometry
from pydantic.dataclasses import dataclass
from pydantic import Field, validate_call

type SomeProp = PropDef | PropsSection


class PropsDict(Mapping[str, SomeProp]):
    _props: Mapping[str, SomeProp]

    def __init__(
        self, props: Mapping[str, SomeProp] | Iterable[tuple[str, SomeProp]] = {}
    ):
        self._props = (
            dict(props) if isinstance(props, Mapping) else {k: v for k, v in props}
        )

    def __and__(self, other: Mapping[str, SomeProp]) -> "PropsDict":
        return self.merge(other)

    def merge(
        self, other: Mapping[str, SomeProp] | Iterable[tuple[str, SomeProp]]
    ) -> "PropsDict":
        result = {}
        other = PropsDict(other)
        for key in self.keys() | other.keys():
            result[key] = merge(self.get(key, None), other.get(key, None))
        return PropsDict(result)

    def set(self, **props: PropDef) -> "PropsDict":
        return self.merge(props)

    def __len__(self) -> int:
        return len(self._props)

    def __iter__(self) -> Iterator[str]:
        return iter(self._props)

    def with_values(self, values: Mapping[str, Any] | None = None) -> "PropVals":
        return PropVals(self, values or {})

    def __getitem__(self, key: str) -> SomeProp:
        return self._props[key]

    def assert_match(self, other: Mapping[str, Any]) -> None:
        errors = []
        for key in self.keys() | other.keys():
            if key not in self:
                errors += [f"Key of input map {key} doesn't exist in self."]
            if key not in other:
                errors += [f"Key of self map {key} doesn't exist in input."]
            if self[key] != other[key]:
                errors += [f"Key {key} doesn't match."]

        if errors:
            raise ValueError("\n".join(errors))


class PropVals(Mapping[str, Any]):
    _props: PropsDict
    _vals: Mapping[str, Any]

    def __init__(self, props: PropsDict, values: Mapping[str, Any] = {}):
        self._props = props
        self._vals = values
        self._assert_values(values)

    def _assert_values(self, other: Mapping[str, Any]) -> None:
        for k, v in other.items():
            if k not in self._props:
                raise ValueError(f"Key {k} not found!")
            value = self._props.get(k, None)
            match value:
                case PropDef():
                    if not value.is_valid(v):
                        raise ValueError(f"Value {v} is not valid for key {k}, {value}")
                case PropsSection():
                    if not isinstance(v, Mapping):
                        raise ValueError(
                            f"Value {v} is not a mapping for prop section {k}, {value}"
                        )

    def merge(self, other: Mapping[str, Any]) -> "PropVals":
        self._assert_values(other)

        return PropVals(self._props, {**self._vals, **other})

    def set(self, **vals: Any) -> "PropVals":
        return self.merge(vals)

    def __len__(self) -> int:
        return len(self._props)

    def __iter__(self) -> Iterator[str]:
        return iter(self._props)

    def __and__(self, other: "PropVals") -> "PropVals":
        return self.merge(other)

    @staticmethod
    def _diff(a: Any, b: Any) -> Any:
        if isinstance(a, PropVals):
            if not isinstance(b, PropVals):
                raise ValueError("Cannot diff PropVals with non-PropVals")
            return a.diff(b)
        if isinstance(b, PropVals):
            raise ValueError("Cannot diff PropVals with non-PropVals")
        if a == b:
            return SAME
        return b

    @validate_call
    def diff(self, other: "PropVals") -> "PropVals":
        self._props.assert_match(other._props)
        out = {}
        for k, v in self._vals:
            match self._props[k]:
                case PropDef():
                    if v != other._vals[k]:
                        out[k] = v
                case PropsSection() as s:
                    if s.recurse:
                        result = PropVals._diff(v, other._vals[k])
                        if result is not SAME:
                            out[k] = result
                    else:
                        if v != other._vals[k]:
                            out[k] = v

        return PropVals(self._props, out)


@dataclass
class PropsSection:
    props: PropsDict
    recurse: bool = field(default=True)
    alias: str | None = field(default=None)
    converter: Callable[["PropsDict"], Any] = field(default=lambda x: x)
    __match_args__ = ("recurse",)
