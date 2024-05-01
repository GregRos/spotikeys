from abc import abstractmethod
from dataclasses import field
from tkinter import Tk, Widget
from types import MappingProxyType
from typing import Any, Callable, Generator, Literal
from attr import dataclass


from src.client.ui.framework.component import Component
from src.client.ui.framework.make_clickthrough import make_clickthrough
from src.client.ui.shadow.core.reconciler.property_dict import compute_values
from src.client.ui.shadow.core.reconciler.reconcile import Reconcile

from src.client.ui.shadow.core.fields import FieldApplyInfo
from src.client.ui.shadow.core.reconciler.property_dict import (
    PropertyDict,
    compute_diff,
)


Mismatch = Literal["different_key", "same_key_different_type", "missing", None]


@dataclass(frozen=True)
class ShadowNode[W: Widget]:
    key: str

    @property
    @abstractmethod
    def tk_type(self) -> str: ...
    def to_property_dict(self) -> PropertyDict:
        from src.client.ui.shadow.core.fields import FieldApplyInfo

        def _to_properties():
            for key in self.__dataclass_fields__:
                field = self.__dataclass_fields__[key]
                metadata = field.metadata
                if not metadata:
                    print(f"Metadata not found for {key}")
                    continue
                if "apply" not in metadata:
                    print(f"ApplyInfo not found for {key}")
                    continue
                apply_info = metadata["apply"]
                if not isinstance(apply_info, FieldApplyInfo):
                    print(f"Invalid apply info for {key} {apply_info}")
                yield apply_info.to_apply_pair(key, getattr(self, key))

        return dict(_to_properties())

    def post_reconcile(self, widget: W):
        pass
