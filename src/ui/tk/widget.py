from abc import abstractmethod
from copy import copy
from dataclasses import dataclass
from itertools import groupby
from types import MappingProxyType
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Callable,
    ClassVar,
    Generator,
    Literal,
    NotRequired,
    Self,
    Unpack,
    override,
)
from src.ui.model.prop import Prop
from src.ui.model.context import Ctx
from src.ui.rendering.renderer import ComponentMount
from src.ui.rendering.stateful_reconciler import StatefulReconciler
from src.ui.model.component import Component
from src.ui.model.prop_dict import PSection
from src.ui.tk.font import Font
from src.ui.tk.make_clickthrough import make_clickthrough


from src.ui.model.shadow_node import ShadowNode, ShadowProps


class WidgetProps(ShadowProps):
    text: Annotated[NotRequired[str], Prop(no_value=" ", subsection="configure")]
    font: Annotated[NotRequired[Font], PSection(recurse=False, name="Font")]
    borderwidth: Annotated[NotRequired[int], Prop(no_value=0, subsection="configure")]
    background: Annotated[
        NotRequired[str], Prop(no_value="#000001", subsection="configure")
    ]
    foreground: Annotated[
        NotRequired[str], Prop(no_value="#ffffff", subsection="configure")
    ]
    justify: Annotated[
        NotRequired[str], Prop(no_value="center", subsection="configure")
    ]
    relief: Annotated[NotRequired[str], Prop(no_value="solid", subsection="configure")]


class PackProps(ShadowProps):
    ipadx: Annotated[NotRequired[int], Prop(no_value=0)]
    ipady: Annotated[NotRequired[int], Prop(no_value=0)]
    fill: Annotated[
        NotRequired[Literal["both", "x", "y", "none"]], Prop(no_value="none")
    ]


class Widget(ShadowNode):

    @PSection(recurse=True)
    def __init__(self, **props: Unpack[WidgetProps]): ...

    @PSection(recurse=False)
    def Pack(self, **props: Unpack[PackProps]) -> None:
        pass

    def _copy(self, **overrides: Any) -> Self:
        clone = copy(self)
        clone._props = self._props.merge(overrides)
        return clone


class Label(Widget):

    pass
