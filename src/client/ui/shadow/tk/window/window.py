import copy
from tkinter import Tk, Widget
from typing import Annotated, Generator, Iterable, Literal, NotRequired, Self, TypedDict, Unpack, override


from src.client.ui.shadow.core.rendering.component import Component
from src.client.ui.shadow.tk.make_clickthrough import make_clickthrough
from src.client.ui.shadow.core.props.prop import prop
from src.client.ui.shadow.core.props.operators import GroupedDict, UncomputedValue
from src.client.ui.shadow.core.props.shadow_node import InitPropsBase, ShadowProps
from src.client.ui.shadow.core.reconciler.stateful_reconciler import StatefulReconciler
from src.client.ui.shadow.tk.widgets.widget import WidgetNode
from src.client.ui.values.geometry import Geometry
from pydantic.dataclasses import dataclass
from pydantic import Field


class Props(InitPropsBase):
    topmost: NotRequired[bool]
    background: NotRequired[str]
    transparent_color: NotRequired[str]
    override_redirect: Annotated[NotRequired[bool], ""]
    
class Geometry(TypedDict):
    x: int
    y: int
    width: int
    height: int
    
class SwTkWindow(ShadowProps, Component[WidgetNode]):
    _geometry: Geometry = Field(init=False)
    _children: tuple[Component[WidgetNode], ...] = Field(init=False)
    topmost: bool = prop("attributes", default=False)
    transparent_color: str | None = prop(
        "attributes", default=None, name="transparentcolor"
    )
    override_redirect: bool = prop("", default=False)
    background: str = prop("configure", default="black")

    def geometry(self, **geometry: Unpack[Geometry]) -> "SwTkWindow":

    @override
    def render(self, _) -> Generator[WidgetNode | Component[WidgetNode], None, None]:
        yield from self.children

    def copy(self) -> Self:
        return self.__class__(**self.__dict__)


@dataclass(kw_only=True)
class WindowComponent(Component[SwTkWindow]):
    pass
