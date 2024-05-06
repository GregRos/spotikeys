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

    key: str = field(default="")
