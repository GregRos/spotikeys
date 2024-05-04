from src.client.ui.shadow.core.props.prop_info import PropInfo


from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, ClassVar, Literal, Self

from src.client.ui.shadow.core.props.prop_info import PropInfo
from src.client.ui.shadow.core.props.grouped_dict import GroupedDict, UncomputedValue


def to_prop(self, key: str, field: Any) -> Any:

    metadata = field.metadata
    if not metadata:
        return None
    prop_info = metadata.get("prop")
    if not isinstance(prop_info, PropInfo):
        print(f"Invalid apply info for {key} {prop_info}")
        return None
    v = UncomputedValue(prop_info.converter, getattr(self, key), prop_info.name or key)
    return prop_info.type, key, v


@dataclass()
class ShadowNode(ABC):
    @staticmethod
    @abstractmethod
    def props_dict() -> GroupedDict[UncomputedValue]: ...

    key: str = field(default="")
    _props: GroupedDict[UncomputedValue] = field(
        init=False,
        compare=False,
        hash=False,
        repr=False,
    )

    def __post_init__(self):

        props = self.props_dict()
        for key in self.__dataclass_fields__:
            field = self.__dataclass_fields__[key]
            match to_prop(self, key, field):
                case None:
                    continue
                case group, key, value:
                    props[group, key] = value

        self._props = props
