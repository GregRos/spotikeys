from typing import Any, Callable, Generator

from src.ui.model import ShadowNode, Ctx, Component
from src.ui.rendering.stateful_reconciler import StatefulReconciler
from src.ui.model.prop_dict import format_superscript


def with_key(node: ShadowNode, key: str) -> ShadowNode:
    return node._copy(key=key)


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
            i = 1

            def on_yielded(node: Component[X] | X):
                node_type = self._reconciler.node_type
                nonlocal rendering, i
                cur_prefix = "".join(
                    [
                        root_prefix,
                        f":{node.key}." if node.key else format_superscript(i),
                        node.__class__.__name__,
                        " ",
                    ]
                )

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

        yield_ = on_yielded_for("")
        yield_(self._mounted)
        return rendering

    def remount(self, root: Component[X]):
        self._mounted = root
        self.force_rerender()

    def force_rerender(self):
        self._reconciler.reconcile(self._compute_render())
