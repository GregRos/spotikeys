from copy import copy
from dataclasses import dataclass
from typing import (
    Annotated,
    Any,
    NotRequired,
    Self,
    Unpack,
    override,
)


from src.ui.model.prop_dict import PSection
from src.ui.model.prop import Prop
from src.ui.model.component import Component
from src.ui.model.shadow_node import (
    InitPropsBase,
    ShadowNode,
)
from src.ui.tk.widget import Widget


class WindowProps(InitPropsBase):
    topmost: Annotated[NotRequired[bool], Prop(subsection="attributes")]
    background: Annotated[NotRequired[str], Prop(subsection="configure")]
    transparent_color: Annotated[
        NotRequired[str], Prop(subsection="attributes", name="transparentcolor")
    ]
    override_redirect: Annotated[NotRequired[bool], Prop()]
    alpha: Annotated[NotRequired[float], Prop(subsection="attributes")]


class Geometry(InitPropsBase):
    x: int
    y: int
    width: int
    height: int


class Window(ShadowNode, Component[Widget]):  # type: ignore

    @PSection(recurse=True)
    def __init__(self, **props: Unpack[WindowProps]): ...

    @override
    def _copy(self, **overrides: Any) -> Self:
        clone = copy(self)
        clone._props = self._props.merge(overrides)
        return clone

    @PSection(recurse=False)
    def Geometry(self, **props: Unpack[Geometry]): ...