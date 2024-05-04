from src.client.ui.shadow.core.props.props_map import ApplyInfo, Diff, DiffMap, PropsMap


from pyrsistent import PMap


from abc import abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Self


@dataclass()
class ShadowNode:
    key: str = field(default="")
    diff_groups: ClassVar[DiffMap]
    _props: PropsMap = field(init=False, compare=False, hash=False, repr=False)

    def __init_subclass__(cls, groups: DiffMap) -> None:
        super().__init_subclass__()
        cls.diff_groups = groups

    def __post_init__(self):
        from src.client.ui.shadow.core.props.field_apply_info import PropInfo

        props_map = PropsMap(self.__class__.diff_groups)
        for key in self.__dataclass_fields__:
            field = self.__dataclass_fields__[key]
            metadata = field.metadata
            if not metadata:
                continue
            prop_info = metadata.get("prop")
            if not isinstance(prop_info, PropInfo):
                print(f"Invalid apply info for {key} {prop_info}")
                continue
            pair = ApplyInfo(
                prop_info.converter, getattr(self, key), prop_info.name or key
            )
            props_map = props_map.set((prop_info.type, key), pair)

        self._props = props_map
