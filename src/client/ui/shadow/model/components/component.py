from __future__ import annotations
import abc
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


from src.client.ui.shadow.model.props.dict.prop_section import PropSection
from src.client.ui.shadow.model.props.dict.read_annotations import (
    make_props_from_annotated,
)
from src.client.ui.shadow.model.props.single.prop_def import PropDef
from src.client.ui.shadow.model.props.dict.props_dict import PropsDict
from src.client.ui.shadow.model.nodes.shadow_node import (
    InitPropsBase,
    ShadowNode,
    ShadowProps,
)
from src.client.ui.shadow.core.context import Ctx, Updatable
from pydantic.dataclasses import dataclass

if TYPE_CHECKING:
    from src.client.ui.framework.tooltip_row import TooltipRow


class ComponentProps(InitPropsBase):
    key: Annotated[NotRequired[str], PropDef(default="")]
    children: Annotated[NotRequired[Tuple[Self, ...]], PropDef(default=())]


@dataclass(kw_only=True)
class Component[Node: ShadowNode](abc.ABC):
    key: str = Field(default="")
    children: Tuple[Component[Node], ...] = Field(default=())

    def _copy(self, **overrides: Any) -> Self:
        return self.__class__(**{**self.__dict__, **overrides})

    def render(self, ctx: Ctx, /) -> Generator[Node | Component[Node], None, None]:
        yield from self.children

    def __getitem__(
        self, children: tuple[Component[Node], ...] | Component[Node]
    ) -> Self:
        children = children if isinstance(children, tuple) else (children,)
        return self._copy(children=children)
