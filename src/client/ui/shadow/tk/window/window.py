import copy
from dataclasses import dataclass, field
from tkinter import Tk, Widget
from typing import Iterable, Literal, Self, override

from pyrsistent import PVector, pvector, v

from src.client.ui.framework.component import Component
from src.client.ui.framework.make_clickthrough import make_clickthrough
from src.client.ui.shadow.core.props.prop import prop
from src.client.ui.shadow.core.props.grouped_dict import GroupedDict, UncomputedValue
from src.client.ui.shadow.core.props.shadow_node import ShadowNode
from src.client.ui.shadow.core.reconciler.stateful_reconciler import StatefulReconciler
from src.client.ui.shadow.tk.widgets.widget import SwTkWidget
from src.client.ui.values.geometry import Geometry


@dataclass(kw_only=True)
class SwTkWindowProps:
    key: str = field(default="")
    width: int = prop("geometry")
    height: int = prop("geometry")
    y: int = prop("geometry")
    x: int = prop("geometry")
    topmost: bool = prop("attributes", default=False)
    transparent_color: str | None = prop(
        "attributes", default=None, name="transparentcolor"
    )
    override_redirect: bool = prop("", default=False)
    background: str = prop("configure", default="black")

    def __getitem__(self, *children: Component[SwTkWidget]) -> "SwTkWindow":
        return SwTkWindow(**self.__dict__, children=children)


@dataclass(kw_only=True)
class SwTkWindow(ShadowNode, SwTkWindowProps):

    @override
    @staticmethod
    def props_dict():
        return GroupedDict[UncomputedValue](
            {
                "geometry": "unit",
                "attributes": "recursive",
                "": "recursive",
                "configure": "recursive",
                "geometry": "unit",
            }
        )

    children: tuple[Component[SwTkWidget], ...] = prop("")

    @property
    def geometry(self) -> Geometry:
        return Geometry(self.width, self.height, self.x, self.y)

    def copy(self) -> Self:
        return self.__class__(**self.__dict__)
