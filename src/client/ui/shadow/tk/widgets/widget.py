from abc import abstractmethod
from dataclasses import dataclass
from itertools import groupby
from tkinter import Label, Tk, Widget
from types import MappingProxyType
from typing import TYPE_CHECKING, Callable, Generator, Literal, Self, override
from src.client.ui.shadow.core.component import Component
from src.client.ui.shadow.tk.make_clickthrough import make_clickthrough


from src.client.ui.shadow.core.props.grouped_dict import GroupedDict, UncomputedValue
from src.client.ui.shadow.core.props.shadow_node import ShadowNode


@dataclass(kw_only=True)
class SwTkWidget(ShadowNode):
    @override
    @staticmethod
    def props_dict() -> GroupedDict[UncomputedValue]:
        return GroupedDict({"configure": "recursive", "pack": "unit"})

    @property
    @abstractmethod
    def tk_type(self) -> str: ...


@dataclass(kw_only=True)
class WidgetComponent(Component[SwTkWidget]):
    pass
