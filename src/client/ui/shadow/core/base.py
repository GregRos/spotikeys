from abc import abstractmethod
from collections.abc import Mapping
from dataclasses import field
from itertools import groupby
from tkinter import Label, Tk, Widget
from types import MappingProxyType
from typing import TYPE_CHECKING, Any, Callable, Generator, Literal, Self, override
from attr import dataclass
from pyrsistent import PMap, m, pmap, pset, v
from src.client.ui.framework.component import Component
from src.client.ui.framework.make_clickthrough import make_clickthrough


from src.client.ui.shadow.core.fields import FieldApplyInfo
from src.client.ui.shadow.core.reconciler.property_dict import ApplyInfo

if TYPE_CHECKING:
    from src.client.ui.shadow.core.reconciler.stateful_reconciler import ResourceRecord


Mismatch = Literal["different_key", "same_key_different_type", "missing", None]
ReconcileType = Literal["update", "get_or_create", "destroy_and_create", "create"]


class PropsMap(Mapping[str, ApplyInfo]):
    def __init__(self, props: PMap[str, ApplyInfo] = PMap()):
        self._map = props

    def compute(self):
        return {
            key: value.converter(value.value) if value.converter else value.value
            for key, value in self._map.items()
        }

    def __getitem__(self, key: str) -> ApplyInfo:
        return self._map[key]

    def set(self, key: str, value: ApplyInfo) -> "PropsMap":
        return PropsMap(self._map.transform(key, value))

    def diff(self, other: "PropsMap") -> "PropsMap":
        result = PMap[str, ApplyInfo]()
        for key, value in self._map.items():
            if key not in other._map or other[key] != value:
                result = result.transform(key, value)
        return PropsMap(result)


@dataclass(kw_only=True)
class ShadowNode:
    key: str = field(default="")
    _props: PMap[str, PropsMap] = field(default_factory=PMap[str, PropsMap])

    def __post_init__(self):
        from src.client.ui.shadow.core.fields import FieldApplyInfo

        a = PropsMap()
        props_map = PMap[str, PropsMap]()
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
            these_props = props_map.get(field_info.type, PropsMap())
            pair = ApplyInfo(field_info.converter, getattr(self, key))
            props_map = props_map.transform(field_info.type, these_props.set(key, pair))

        self._props = props_map

    @abstractmethod
    def get_compatibility(
        self, prev: Self | None | "ResourceRecord[Self, Any]"
    ) -> Literal["update", "replace", "recreate"]: ...


@dataclass(kw_only=True)
class ShadowTkWidget(ShadowNode):
    @property
    @abstractmethod
    def tk_type(self) -> str: ...

    @override
    def get_compatibility(self, prev) -> Literal["update", "replace", "recreate"]:
        prev = prev.node if isinstance(prev, ResourceRecord) else prev
        if prev is None:
            return "recreate"
        if self.tk_type != prev.tk_type:
            return "replace"
        return "update"
