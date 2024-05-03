from ast import TypeAlias
from collections.abc import Mapping
from dataclasses import dataclass, field
from itertools import groupby
from typing import TYPE_CHECKING, Any, Callable, TypeVar

from pyrsistent import m, pmap


@dataclass(frozen=True)
class ApplyInfo:
    converter: Callable[[Any], Any] | None
    value: Any


@dataclass(frozen=True)
class ApplyKey:
    stage: str
    prop_name: str
