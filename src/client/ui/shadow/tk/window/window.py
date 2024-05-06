import copy
from dataclasses import dataclass, field
from tkinter import Tk, Widget
from typing import Generator, Iterable, Literal, Self, override


from src.client.ui.shadow.core.rendering.component import Component
from src.client.ui.shadow.tk.make_clickthrough import make_clickthrough
from src.client.ui.shadow.core.props.prop import prop
from src.client.ui.shadow.core.props.grouped_dict import GroupedDict, UncomputedValue
from src.client.ui.shadow.core.props.shadow_node import ShadowNode
from src.client.ui.shadow.core.reconciler.stateful_reconciler import StatefulReconciler
from src.client.ui.shadow.tk.widgets.widget import SwTkWidget
from src.client.ui.values.geometry import Geometry


@dataclass(kw_only=True)
class SwTkWindow(ShadowNode, Component[SwTkWidget]):
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
    children: tuple[Component[SwTkWidget], ...] = prop("", default=())

    @override
    def render(self, _) -> Generator[SwTkWidget | Component[SwTkWidget], None, None]:
        yield from self.children

    @property
    def geometry(self) -> Geometry:
        return Geometry(self.width, self.height, self.x, self.y)

    def copy(self) -> Self:
        return self.__class__(**self.__dict__)


@dataclass(kw_only=True)
class WindowComponent(Component[SwTkWindow]):
    pass
