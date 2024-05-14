from __future__ import annotations
import abc
from dataclasses import dataclass, field
from tkinter import Tk, Widget
from types import SimpleNamespace
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Callable,
    Generator,
    NotRequired,
    Self,
    Tuple,
    TypedDict,
    Unpack,
    override,
)


from src.client.ui.shadow.core.props.single.prop_def import PropDef
from src.client.ui.shadow.core.props.dict.props_dict import PropsDict
from src.client.ui.shadow.core.reconciler.shadow_node import (
    InitPropsBase,
    ShadowNode,
    ShadowProps,
)
from src.client.ui.shadow.core.context import Ctx, Updatable

if TYPE_CHECKING:
    from src.client.ui.framework.tooltip_row import TooltipRow


class ComponentProps(InitPropsBase):
    key: Annotated[NotRequired[str], PropDef(default="")]
    children: Annotated[NotRequired[Tuple[Self, ...]], PropDef(default=())]


@dataclass(kw_only=True)
class Component[Node: ShadowNode](abc.ABC):
    _props: PropsDict

    def __post_init__(self) -> None:
        my_dict = {
            k: v
            for k, v in self.__dict__.items()
            if (x := self.__dataclass_fields__.get(k, None)) and "prop" in x.metadata
        }
        self._props = PropsDict(my_dict)

    @property
    def key(self) -> str:
        return self._props["key"]

    def _copy(self, **overrides: Any) -> Self:
        return self.__class__(**self._props.merge(overrides))

    def render(self, ctx: Ctx, /) -> Generator[Node | Component[Node], None, None]:
        yield from self._props["children"]

    def __getitem__(
        self, children: tuple[Component[Node], ...] | Component[Node]
    ) -> Self:
        children = children if isinstance(children, tuple) else (children,)
        new_props = self._props.set("children", children)
        return self._copy(_props=new_props)
