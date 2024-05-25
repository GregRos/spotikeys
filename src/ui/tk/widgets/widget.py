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
from src.ui.core.context import Ctx
from src.ui.core.renderer import ComponentMount
from src.ui.core.stateful_reconciler import StatefulReconciler
from src.ui.model.component import Component
from src.ui.model.props.dict.props_dict import section
from src.ui.tk.make_clickthrough import make_clickthrough


from src.ui.model.shadow_node import ShadowNode, ShadowProps
from src.ui.tk.widgets.props import PackProps, WidgetProps


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
