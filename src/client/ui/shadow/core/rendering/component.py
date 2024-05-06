from __future__ import annotations
import abc
from dataclasses import dataclass, field
from tkinter import Tk, Widget
from types import SimpleNamespace
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generator,
    Self,
    Tuple,
    TypedDict,
    Unpack,
    override,
)


from src.client.ui.shadow.core.props.prop import prop
from src.client.ui.shadow.core.props.shadow_node import ShadowNode
from src.client.ui.shadow.core.state import Ctx, Updatable

if TYPE_CHECKING:
    from src.client.ui.framework.tooltip_row import TooltipRow


@dataclass(kw_only=True)
class Component[Node: ShadowNode](abc.ABC):
    key: str = field(default="")
    children: tuple[Component[Node], ...] = prop("", default=())

    def as_dict(self) -> dict[str, Any]:
        my_dict = {
            k: v
            for k, v in self.__dict__.items()
            if (x := self.__dataclass_fields__.get(k, None)) and "prop" in x.metadata
        }
        return my_dict

    def render(self, ctx: Ctx, /) -> Generator[Node | Component[Node], None, None]:
        yield from self.children

    def __getitem__(
        self, children: tuple[Component[Node], ...] | Component[Node]
    ) -> Self:
        children = children if isinstance(children, tuple) else (children,)
        my_dict = self.as_dict()
        my_dict["children"] = children
        return self.__class__(**my_dict)


def render_recursively[
    Node: ShadowNode
](
    node_type: type[Node],
    prefix: str,
    component: "Component[Node]",
) -> Generator[
    Node, None, None
]:
    prefix = ".".join([prefix, component.__class__.__name__])

    for i, child in enumerate(component.render(Ctx())):
        cur_prefix = ":".join([prefix, child.key or str(i)])
        if isinstance(child, node_type):
            child.key = cur_prefix
            yield child
        elif isinstance(child, Component):
            yield from render_recursively(node_type, cur_prefix, child)
        else:
            raise TypeError(f"Expected {node_type} but got {child}")
