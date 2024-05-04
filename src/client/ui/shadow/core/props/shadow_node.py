from src.client.ui.shadow.core.props.props_map import ApplyInfo, DiffMap, PropsMap


from pyrsistent import PMap


from abc import abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Literal, Self

if TYPE_CHECKING:
    from src.client.ui.shadow.core.reconciler.record import ResourceRecord


@dataclass()
class ShadowNode:
    key: str = field(default="")
    _props: PropsMap = field(init=False)

    @staticmethod
    @abstractmethod
    def diff_groups() -> DiffMap: ...

    def __post_init__(self):
        from src.client.ui.shadow.core.props.field_apply_info import FieldApplyInfo

        props_map = PropsMap(self.__class__.diff_groups())
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
            pair = ApplyInfo(
                field_info.converter, getattr(self, key), field_info.name or key
            )
            props_map = props_map.set((field_info.type, key), pair)

        self._props = props_map

    @abstractmethod
    def get_compatibility(
        self, prev: Self | None | "ResourceRecord[Self, Any]"
    ) -> Literal["update", "replace", "recreate"]: ...
