from dataclasses import dataclass

from src.client.ui.shadow.core.props.shadow_node import ShadowNode
from src.client.ui.shadow.core.rendering.component import Component
from src.client.ui.shadow.core.state import Updatable


@dataclass
class RenderRecord[Node: ShadowNode]:
    component: Component
    rendered: tuple[Node, ...]


class Rendered:
    _last_render: dict[str, RenderRecord]


class RecursiveRenderer:
    _last_render: dict[str, RenderRecord]

    def __init__(self, node_type: type[ShadowNode], prefix: str, context: Updatable):
        self.node_type = node_type
        self.prefix = prefix
        self._last_render = {}
        self.context = context

    def render(self, component: Component):
        pass
