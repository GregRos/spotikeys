from src.client.ui.shadow.core.props.props_map import ApplyInfo, PropsMap
from src.client.ui.shadow.core.reconciler.stateful_reconciler import ResourceRecord


from attr import dataclass
from pyrsistent import PMap


from abc import abstractmethod
from dataclasses import field
from typing import Any, Literal, Self


@dataclass(kw_only=True)
class ShadowNode:
    key: str = field(default="")
    _props: PMap[str, PropsMap] = field(default_factory=PMap[str, PropsMap])

    def __post_init__(self):
        from src.client.ui.shadow.core.props.field_apply_info import FieldApplyInfo

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
