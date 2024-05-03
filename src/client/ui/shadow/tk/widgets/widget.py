from abc import abstractmethod
from itertools import groupby
from tkinter import Label, Tk, Widget
from types import MappingProxyType
from typing import TYPE_CHECKING, Callable, Generator, Literal, Self, override
from attr import dataclass
from pyrsistent import m, pmap
from src.client.ui.framework.component import Component
from src.client.ui.framework.make_clickthrough import make_clickthrough


from src.client.ui.shadow.core.props.props_map import DiffMap
from src.client.ui.shadow.core.props.shadow_node import ShadowNode

if TYPE_CHECKING:
    from src.client.ui.shadow.core.reconciler.actions import ResourceRecord


@dataclass(kw_only=True)
class SwTkWidget(ShadowNode):
    @property
    @abstractmethod
    def tk_type(self) -> str: ...
    @staticmethod
    def diff_groups() -> DiffMap:
        return pmap({"configure": "recursive"})

    @override
    def get_compatibility(self, prev) -> Literal["update", "replace", "recreate"]:
        prev = prev.node if isinstance(prev, ResourceRecord) else prev
        if prev is None:
            return "recreate"
        if self.tk_type != prev.tk_type:
            return "replace"
        return "update"
