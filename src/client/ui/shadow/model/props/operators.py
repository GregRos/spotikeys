from abc import abstractmethod
from dataclasses import MISSING, dataclass, field
from numbers import Number
from typing import (
    Any,
    Callable,
    Iterable,
    Iterator,
    Literal,
    Protocol,
    Self,
    TypeGuard,
    cast,
    overload,
    override,
    runtime_checkable,
)


from collections.abc import Mapping
from typing_extensions import runtime

from pydantic import validate_call
from pydantic_core import Some


class Result:
    def __init__(self, name: str, truthy: bool):
        self.name = name
        self.truthy = truthy

    def __bool__(self):
        return self.truthy

    def __eq__(self, other: Any):
        return other is self

    def __str__(self):
        return f"!{self.name}!"


SAME = Result("SAME", True)
REMOVED = Result("REMOVED", False)


@runtime_checkable
class Computable(Protocol):
    @abstractmethod
    def compute(self, key: str) -> tuple[str, Any] | None: ...

    @abstractmethod
    def __eq__(self, other: object) -> bool: ...


@runtime_checkable
class Diffable(Protocol):
    @abstractmethod
    def delta_from(self, other: Self, /) -> Any: ...

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        return isinstance(other, self.__class__) and self.delta_from(other) is SAME


def compute(key: str, value: object, /) -> tuple[str, Any] | None:
    def compute_dict(key: str, value: Mapping[str, Any], /):
        result = {}
        for key2, val in value.items():
            p = compute(key2, val)
            if not p:
                continue
            key2_r, v = p
            result[key2_r] = v
        if not result:
            return None
        return key, result

    def compute_list(key: str, value: Iterable[object], /):
        result = []
        for i, val in enumerate(value):
            p = compute(str(i), val)
            if not p:
                continue
            _, v = p
            result.append(v)
        if not result:
            return None
        return key, result

    if isinstance(value, Computable):
        result = value.compute(key)
        if not result:
            return result
        return compute(key, value)
    if isinstance(value, list) or isinstance(value, tuple) or isinstance(value, set):
        return compute_list(key, value)
    if isinstance(value, Mapping):
        return compute_dict(key, value)
    return key, value


def diff(left: object, right: object, /) -> object:
    def diff_dicts(
        left: Mapping[str, Any], right: Mapping[str, Any], /
    ) -> Mapping[str, Any]:
        result = {}
        for key in left.keys() | right.keys():
            if key not in right:
                result[key] = REMOVED
                continue
            if key not in left:
                result[key] = right[key]
                continue
            l_val, r_val = left[key], right[key]
            difference = diff(l_val, r_val)
            if difference is not SAME:
                result[key] = difference
        return result

    if isinstance(left, Diffable) and isinstance(right, Diffable):
        return left.delta_from(right)

    if isinstance(right, Mapping) and isinstance(left, Mapping):
        return diff_dicts(left, right) or SAME

    if right == left:
        return SAME
    return right
