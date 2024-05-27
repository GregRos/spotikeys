from typing import Any, Callable, Generator

from src.ui.model.shadow_node import ShadowNode
from src.ui.rendering.stateful_reconciler import StatefulReconciler
from src.ui.model.component import Component
from src.ui.model.context import Ctx, Updatable
from pydantic.dataclasses import dataclass


def with_key(node: ShadowNode, key: str) -> ShadowNode:
    return node._copy(key=key)


def wrap_root(children: tuple[Component, ...] | Component) -> Component:
    return (
        Component(key="GenericRoot", children=children)
        if isinstance(children, tuple)
        else children
    )


class ComponentMount[X: ShadowNode]:
    _reconciler: StatefulReconciler
    _mounted: Component

    def __init__(
        self, reconciler: StatefulReconciler, context: Ctx, root: Component[X]
    ):
        self._reconciler = reconciler
        self.context = context
        self._mounted = root

    def __call__(self, **ctx_args: Any):
        self.context(**ctx_args)
        return self.context

    def _compute_render(self):
        rendering = ()

        def on_yielded_for(root_prefix: str):
            i = 0

            def on_yielded(node: Component[X] | X):
                node_type = self._reconciler.node_type
                nonlocal rendering, i
                cur_prefix = ":".join([root_prefix, node.key or str(i)])
                i += 1
                if isinstance(node, node_type):  # type: ignore
                    rendering += (with_key(node, cur_prefix),)
                elif isinstance(node, Component):
                    node.render(on_yielded_for(cur_prefix), self.context)
                else:
                    raise TypeError(
                        f"Expected render method to return {node_type} or Component, but got {type(node)}"
                    )

            return on_yielded

        self._mounted.render(on_yielded_for(""), self.context)
        return rendering

    def remount(self, root: tuple[Component[X], ...] | Component[X]):
        self._mounted = wrap_root(root)
        self.force_rerender()

    def force_rerender(self):
        self._reconciler.reconcile(self._compute_render())
