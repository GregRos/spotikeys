from abc import abstractmethod
from copy import copy
from dataclasses import dataclass
from itertools import groupby
from tkinter import Label, Tk, Widget
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    ClassVar,
    Generator,
    Literal,
    Self,
    Unpack,
    override,
)
from src.client.ui.shadow.core.context import Ctx
from src.client.ui.shadow.core.renderer import ComponentMount
from src.client.ui.shadow.core.stateful_reconciler import StatefulReconciler
from src.client.ui.shadow.model.components.component import Component
from src.client.ui.shadow.model.props.dict.props_dict import section
from src.client.ui.shadow.tk.make_clickthrough import make_clickthrough


from src.client.ui.shadow.model.nodes.shadow_node import ShadowNode, ShadowProps
from src.client.ui.shadow.tk.widgets.props import PackProps, WidgetProps


class WidgetNode(ShadowNode):
    tk_type: ClassVar[str]

    def __init_subclass__(cls, tk_type: str) -> None:
        cls.tk_type = tk_type
        return super().__init_subclass__()

    @section(recurse=True).setter
    def __init__(self, **props: Unpack[WidgetProps]): ...

    @section(recurse=False).setter
    def pack(self, **props: Unpack[PackProps]) -> None:
        pass

    def _copy(self, **overrides: Any) -> Self:
        clone = copy(self)
        clone._props = self._props.merge(overrides)
        return clone


class LabelNode(WidgetNode, tk_type="Label"):
    pass


@dataclass(kw_only=True)
class WidgetComponent(Component[WidgetNode]):
    pass
