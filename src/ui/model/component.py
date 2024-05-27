from __future__ import annotations
import abc
from dataclasses import dataclass, field
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Callable,
    ClassVar,
    Generator,
    NotRequired,
    Self,
    Tuple,
    TypedDict,
    Unpack,
    override,
)


from src.ui.model.prop import Prop
from src.ui.model.prop_dict import PDict
from src.ui.model.shadow_node import (
    InitPropsBase,
    ShadowNode,
    ShadowProps,
)
from src.ui.model.context import Ctx, Updatable


class ComponentProps(InitPropsBase):
    key: Annotated[NotRequired[str], Prop(no_value="")]
    children: Annotated[NotRequired[Tuple[Self, ...]], Prop(no_value=())]


@dataclass(kw_only=True)
class Component[Node: ShadowNode](abc.ABC):
    key: str = field(default="")

    def _copy(self, **overrides: Any) -> Self:
        return self.__class__(**{**self.__dict__, **overrides})

    def render(self, yld: Callable[[Any], None], ctx: Ctx, /): ...
