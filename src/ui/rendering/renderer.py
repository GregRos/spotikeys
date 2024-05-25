from typing import Callable, Generator

from src.ui.model.shadow_node import ShadowNode
from src.ui.rendering.stateful_reconciler import StatefulReconciler
from src.ui.model.component import Component
from src.ui.rendering.context import Ctx, Updatable
from pydantic.dataclasses import dataclass


def with_key(node: ShadowNode, key: str) -> ShadowNode:
    return node._copy(key=key)


def wrap_root(children: tuple[Component, ...] | Component) -> Component:
    return (
        Component(key="GenericRoot", children=children)
        if isinstance(children, tuple)
        else children
    )


class ComponentMount:
    _reconciler: StatefulReconciler
    _mounted: Component

    def __init__(self, reconciler: StatefulReconciler, context: Ctx, root: Component):
        self._reconciler = reconciler
        self.context = context
        self._mounted = root
        self.context += lambda _: self.force_rerender()

    def _compute_render(self):
        def _render(
            cur_prefix: str, root: Component | tuple[Component, ...]
        ) -> Generator[ShadowNode, None, None]:
            node_type = self._reconciler.node_type
            root = root if isinstance(root, Component) else wrap_root(root)
            cur_prefix = ".".join([cur_prefix, root.__class__.__name__])
            for i, child in enumerate(root.render(self.context)):
                cur_prefix = ":".join([cur_prefix, child.key or str(i)])
                if isinstance(child, node_type):  # type: ignore
                    yield with_key(child, cur_prefix)
                elif isinstance(child, Component):
                    yield from _render(cur_prefix, child)
                else:
                    raise TypeError(
                        f"Expected render method to return {node_type} or Component, but got {type(child)}"
                    )

        return (*_render("", self._mounted),)

    def remount(self, root: tuple[Component, ...] | Component):
        self._mounted = wrap_root(root)
        self.force_rerender()

    def force_rerender(self):
        self._reconciler.reconcile(self._compute_render())
