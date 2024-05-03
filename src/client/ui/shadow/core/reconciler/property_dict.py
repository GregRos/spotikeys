from ast import TypeAlias
from collections.abc import Mapping
from dataclasses import dataclass, field
from itertools import groupby
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from pyrsistent import m, pmap


@dataclass(frozen=True)
class ApplyInfo[X]:
    converter: Callable[[X], Any] | None
    value: X



@dataclass(frozen=True)
class ApplyKey:
    stage: str
    prop_name: str


class PropertyDict(dict[ApplyKey, ApplyInfo[Any]]):


