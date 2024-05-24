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
    ClassVar,
    Generator,
    NotRequired,
    Self,
    Tuple,
    TypedDict,
    Unpack,
    override,
)

from pydantic import Field


from src.client.ui.shadow.model.props.from_type.read_annotations import (
    get_sections,
)
from src.client.ui.shadow.model.props.single.prop_def import PropDef
from src.client.ui.shadow.model.props.dict.props_dict import PropsDict
from src.client.ui.shadow.model.nodes.shadow_node import (
    InitPropsBase,
    ShadowNode,
    ShadowProps,
)
from src.client.ui.shadow.core.context import Ctx, Updatable


class ComponentProps(InitPropsBase):
    key: Annotated[NotRequired[str], PropDef(default="")]
    children: Annotated[NotRequired[Tuple[Self, ...]], PropDef(default=())]


@dataclass(kw_only=True)
class Component[Node: ShadowNode](abc.ABC):
    key: str = field(default="")
    children: Tuple[Component[Node], ...] = field(default=())

    def _copy(self, **overrides: Any) -> Self:
        return self.__class__(**{**self.__dict__, **overrides})

    def render(self, ctx: Ctx, /) -> Generator[Node | Component[Node], None, None]:
        yield from self.children

    def __getitem__(
        self, children: tuple[Component[Node], ...] | Component[Node]
    ) -> Self:
        children = children if isinstance(children, tuple) else (children,)
        return self._copy(children=children)