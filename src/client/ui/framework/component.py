from __future__ import annotations
import abc
from dataclasses import dataclass
from tkinter import Tk, Widget
from typing import TYPE_CHECKING, Any, Generator, Tuple, TypedDict, Unpack, override

from attr import field, frozen

from src.client.ui.binding.active_value import ActiveValue
from src.client.ui.shadow.core.props.shadow_node import ShadowNode

if TYPE_CHECKING:
    from src.client.ui.framework.tooltip_row import TooltipRow


@dataclass
class Component[Node: ShadowNode](
    abc.ABC,
):
    key = field(default="<auto>")

    @abc.abstractmethod
    def render(
        self,
    ) -> Generator[Node | Component[Node], None, None]: ...


def render_recursively[
    Node: ShadowNode
](prefix: str, component: "Component[Node]") -> Generator[Node, None, None]:
    prefix = ".".join([prefix, component.__class__.__name__])
    for i, child in enumerate(component.render()):
        cur_prefix = ":".join([prefix, child.key or str(i)])
        if isinstance(child, Component):
            yield from render_recursively(cur_prefix, child)
        else:
            child.key = cur_prefix
            yield child
