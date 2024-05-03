from abc import abstractmethod
from collections.abc import Mapping
from dataclasses import field
from itertools import groupby
from tkinter import Label, Tk, Widget
from types import MappingProxyType
from typing import Any, Callable, Generator, Literal, Self, override
from attr import dataclass
from pyrsistent import PMap, m, pmap, pset, v
from src.client.ui.framework.component import Component
from src.client.ui.framework.make_clickthrough import make_clickthrough


from src.client.ui.shadow.core.fields import FieldApplyInfo
from src.client.ui.shadow.core.reconciler.property_dict import (
    ApplyInfo,
    PropertyDict,
)


Mismatch = Literal["different_key", "same_key_different_type", "missing", None]
ReconcileType = Literal["update", "get_or_create", "destroy_and_create", "create"]


@dataclass(kw_only=True)
class ShadowNode:
    key: str = field(default="")
    _props: PMap[str, PMap[str, ApplyInfo]] = field(default_factory=PMap)

    def __post_init__(self):
        from src.client.ui.shadow.core.fields import FieldApplyInfo

        props = PMap[str, PMap[str, ApplyInfo]]()
        for key in self.__dataclass_fields__:
            field = self.__dataclass_fields__[key]
            metadata = field.metadata
            if not metadata:
                print(f"Metadata not found for {key}")
                continue
            if "apply" not in metadata:
                print(f"ApplyInfo not found for {key}")
                continue
            field_info = metadata["apply"]
            if not isinstance(field_info, FieldApplyInfo):
                print(f"Invalid apply info for {key} {field_info}")
                continue

            pair = ApplyInfo(field_info.converter, getattr(self, key))
            props = props.transform((field_info.type, key), pair)

        self._props = props

    def _values(self, type: str):
        return self._props.get(type, PMap[str, ApplyInfo]())

    def _diff_from(self, type: str, other: "ShadowNode"):
        my_props = self._values(type)
        other_props = other._values(type)
        result = dict()
        for key, v in other_props.items():
            if key not in my_props or my_props[key] != v:
                result[key] = v
        return result

    @abstractmethod
    def get_compatibility(
        self, prev: Self | None
    ) -> Literal["update", "replace", "recreate"]: ...


@dataclass(kw_only=True)
class ShadowTkWidget(ShadowNode):
    @property
    @abstractmethod
    def tk_type(self) -> str: ...

    @override
    def get_compatibility(
        self, prev: Self | None
    ) -> Literal["update", "replace", "recreate"]:
        if prev is None:
            return "recreate"
        if self.tk_type != prev.tk_type:
            return "replace"
        return "update"
