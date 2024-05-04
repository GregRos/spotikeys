from __future__ import annotations
import abc
from dataclasses import dataclass, field
from tkinter import Tk, Widget
from typing import (
    TYPE_CHECKING,
    Any,
    Generator,
    Self,
    Tuple,
    TypedDict,
    Unpack,
    override,
)


from src.client.ui.shadow.core.props.shadow_node import ShadowNode

if TYPE_CHECKING:
    from src.client.ui.framework.tooltip_row import TooltipRow


@dataclass(kw_only=True)
class Component[Node: ShadowNode]:

    key: str = field(default="")

    @abc.abstractmethod
    def render(
        self,
    ) -> Generator[Node | Component[Node], None, None]: ...


@dataclass(kw_only=True)
class ContainerComponent[Node: ShadowNode](Component[Node]):
    children: tuple[Component[Node], ...]

    def render(self) -> Generator[Node | Component[Node], None, None]:
        for child in self.children:
            yield child

    def __getitem__(
        self, children: tuple[Component[Node], ...] | Component[Node]
    ) -> Self:
        children = children if isinstance(children, tuple) else (children,)
        my_dict = {
            k: v
            for k, v in self.__dict__.items()
            if (x := self.__dataclass_fields__.get(k, None)) and x.metadata
        }
        my_dict["children"] = children
        return self.__class__(**my_dict)


def render_recursively[
    Node: ShadowNode
](node_type: type[Node], prefix: str, component: "Component[Node]") -> Generator[
    Node, None, None
]:
    prefix = ".".join([prefix, component.__class__.__name__])
    for i, child in enumerate(component.render()):
        cur_prefix = ":".join([prefix, child.key or str(i)])
        if isinstance(child, node_type):
            child.key = cur_prefix
            yield child
        elif isinstance(child, Component):
            yield from render_recursively(node_type, cur_prefix, child)
        else:
            raise TypeError(f"Expected {node_type} but got {child}")
