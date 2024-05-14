from abc import abstractmethod
from dataclasses import dataclass
from itertools import groupby
from tkinter import Label, Tk, Widget
from types import MappingProxyType
from typing import TYPE_CHECKING, Callable, Generator, Literal, Self, override
from src.client.ui.shadow.core.rendering.component import Component
from src.client.ui.shadow.tk.make_clickthrough import make_clickthrough


from src.client.ui.shadow.core.props.operators import GroupedDict, UncomputedValue
from src.client.ui.shadow.core.reconciler.shadow_node import ShadowNode, ShadowProps


@dataclass(kw_only=True)
class WidgetNode(ShadowNode["WidgetNode"]):

    @property
    @abstractmethod
    def tk_type(self) -> str: ...


@dataclass(kw_only=True)
class WidgetComponent(Component[WidgetNode]):
    pass
