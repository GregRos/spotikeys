from dataclasses import dataclass
from typing import Callable, Generator

from src.client.ui.shadow.core.reconciler.shadow_node import ShadowNode
from src.client.ui.shadow.core.reconciler.stateful_reconciler import StatefulReconciler
from src.client.ui.shadow.core.rendering.component import Component
from src.client.ui.shadow.core.context import Ctx, Updatable


@dataclass
class RenderRecord[Node: ShadowNode]:
    component: Component
    rendered: tuple[Node, ...]


class Rendered:
    _last_render: dict[str, RenderRecord]


def with_key(node: ShadowNode, key: str) -> ShadowNode:
    return node._copy(key=key)


class ComponentMount:
    _reconciler: StatefulReconciler
    _mounted: Component

    def __init__(self, reconciler: StatefulReconciler, context: Ctx):
        self._reconciler = reconciler
        self.context = context
        self.context += self._on_ctx_changed

    def _on_ctx_changed(self, updatable: Updatable):
        if self._mounted:
            self.rerender()

    def compute_render(self):
        def _render(
            cur_prefix: str, root: Component
        ) -> Generator[ShadowNode, None, None]:
            node_type = self._reconciler.node_type

            cur_prefix = ".".join([cur_prefix, root.__class__.__name__])
            for i, child in enumerate(root.render(self.context)):
                cur_prefix = ":".join([cur_prefix, child.key or str(i)])
                if isinstance(child, node_type):
                    yield with_key(child, cur_prefix)
                elif isinstance(child, Component):
                    yield from _render(cur_prefix, child)
                else:
                    raise TypeError(
                        f"Expected render method to return {node_type} or Component, but got {type(child)}"
                    )

        return (*_render("", self._mounted),)

    def rerender(self):
        self._reconciler.reconcile(self.compute_render())

    def mount(self, root: Component):
        self._mounted = root
        self.rerender()
