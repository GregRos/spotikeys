import copy
from tkinter import Tk, Widget
from typing import (
    Annotated,
    Any,
    Generator,
    Iterable,
    Literal,
    NotRequired,
    Self,
    TypedDict,
    Unpack,
    override,
)


from src.client.ui.shadow.core.props.single.prop_def import PropDef
from src.client.ui.shadow.core.props.dict.prop_section import PropSection
from src.client.ui.shadow.core.props.dict.read_annotations import section_setter
from src.client.ui.shadow.core.rendering.component import Component
from src.client.ui.shadow.tk.make_clickthrough import make_clickthrough
from src.client.ui.shadow.core.reconciler.shadow_node import (
    InitPropsBase,
    ShadowNode,
    ShadowProps,
)
from src.client.ui.shadow.core.reconciler.stateful_reconciler import StatefulReconciler
from src.client.ui.shadow.tk.widgets.widget import WidgetNode
from pydantic.dataclasses import dataclass
from pydantic import Field


class WindowProps(InitPropsBase):
    topmost: Annotated[NotRequired[bool], PropDef(section="configure")]
    background: Annotated[NotRequired[bool], PropDef(section="configure")]
    transparent_color: Annotated[NotRequired[str], PropDef(section="configure")]
    override_redirect: NotRequired[bool]


class Geometry(InitPropsBase):
    x: int
    y: int
    width: int
    height: int


class SwTkWindow(ShadowNode, Component[WidgetNode]):

    @PropSection(diff_mode="recursive").section_setter
    def __init__(self, **props: Unpack[WindowProps]): ...

    @PropSection(diff_mode="simple").section_setter
    def geometry(self, **props: Unpack[Geometry]): ...

    @override
    def _copy(self, **overrides: Any) -> Self:
        return self.__class__(**self._props.merge(overrides))


@dataclass(kw_only=True)
class WindowComponent(Component[SwTkWindow]):
    pass
