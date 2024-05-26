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
from src.ui.model.prop_dict import section
from src.ui.tk.font import Font
from src.ui.tk.make_clickthrough import make_clickthrough


from src.ui.model.shadow_node import ShadowNode, ShadowProps


class WidgetProps(ShadowProps):
    text: Annotated[NotRequired[str], Prop(default=" ", parent="configure")]
    font: Annotated[
        NotRequired[Font],
        Prop(
            default=Font("Courier New", 18, "normal"),
            parent="configure",
            converter=lambda x: x.to_tk(),
        ),
    ]
    borderwidth: Annotated[NotRequired[int], Prop(default=0, parent="configure")]
    background: Annotated[NotRequired[str], Prop(default="#000001", parent="configure")]
    foreground: Annotated[NotRequired[str], Prop(default="#ffffff", parent="configure")]
    justify: Annotated[NotRequired[str], Prop(default="center", parent="configure")]
    relief: Annotated[NotRequired[str], Prop(default="solid", parent="configure")]


class PackProps(ShadowProps):
    ipadx: Annotated[NotRequired[int], Prop(default=0)]
    ipady: Annotated[NotRequired[int], Prop(default=0)]
    fill: Annotated[
        NotRequired[Literal["both", "x", "y", "none"]], Prop(default="none")
    ]


class Widget(ShadowNode):
    tk_type: ClassVar[str]

    def __init_subclass__(cls, tk_type: str) -> None:
        cls.tk_type = tk_type
        return super().__init_subclass__()

    @section(recurse=True)
    def __init__(self, **props: Unpack[WidgetProps]): ...

    @section(recurse=False)
    def pack(self, **props: Unpack[PackProps]) -> None:
        pass

    def _copy(self, **overrides: Any) -> Self:
        clone = copy(self)
        clone._props = self._props.merge(overrides)
        return clone


class Label(Widget, tk_type="Label"):
    pass
