from abc import abstractmethod
from dataclasses import dataclass
from itertools import groupby
from tkinter import Label, Tk, Widget
from types import MappingProxyType
from typing import TYPE_CHECKING, Callable, Generator, Literal, Self, override
from src.client.ui.shadow.core.context import Ctx
from src.client.ui.shadow.core.renderer import ComponentMount
from src.client.ui.shadow.core.stateful_reconciler import StatefulReconciler
from src.client.ui.shadow.model.components.component import Component
from src.client.ui.shadow.tk.make_clickthrough import make_clickthrough


from src.client.ui.shadow.model.nodes.shadow_node import ShadowNode, ShadowProps


@dataclass(kw_only=True)
class WidgetNode(ShadowNode):

    @property
    @abstractmethod
    def tk_type(self) -> str: ...


@dataclass(kw_only=True)
class WidgetComponent(Component[WidgetNode]):
    pass
