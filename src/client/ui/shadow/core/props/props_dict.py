from collections.abc import Mapping
from copy import copy
from dataclasses import MISSING, _MISSING_TYPE
from types import SimpleNamespace
from typing import (
    Any,
    Callable,
    Concatenate,
    Iterator,
    Literal,
    NotRequired,
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

from src.client.ui.shadow.core.props.operators import (
    SAME,
    Computable,
    Diffable,
    diff,
)
from src.client.ui.shadow.core.props.props import (
    JustValue,
    PropDef,
    PropValue,
    norm_props,
)
from src.client.ui.values.geometry import Geometry
from pydantic.dataclasses import dataclass
from pydantic import Field, validate_call


class PropsDict(Mapping[str, PropValue]):

    def __init__(self, props: Mapping[str, PropValue | PropDef | JustValue]):
        self._props = props

    def copy(self) -> "PropsDict":
        return PropsDict(copy(self._props))

    @validate_call
    def merge(self, other: Mapping[str, PropDef | PropValue | Any]) -> "PropsDict":
        normalize_other = {
            k: v if isinstance(v, PropValue) or isinstance(v, PropDef) else JustValue(v)
            for k, v in other.items()
        }
        return PropsDict(norm_props(self._props, normalize_other))

    def set(self, key: str, value: PropValue | Any | PropDef) -> "PropsDict":
        return self.merge({key: value})

    @validate_call
    def __len__(self) -> int:
        return len(self._props)

    def __iter__(self) -> Iterator[str]:
        return iter(self._props)

    @validate_call
    def __getitem__(self, key: str | tuple[str, ...]) -> Any:
        cur = self._props
        path = []
        for k in key:
            path += [k]
            path_str = ".".join(path)
            assert isinstance(
                cur, Mapping
            ), f"Expected map at {path_str}, got {type(cur)}"
        return cur
