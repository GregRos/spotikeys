from typing import Any, Callable, Generator, Iterable

from src.ui.model import ShadowNode, Ctx, Component
from src.ui.rendering.stateful_reconciler import StatefulReconciler
from src.ui.model.prop_dict import format_superscript
from ui.model.render_trace import RenderFrame, RenderTrace


def with_trace(node: ShadowNode, trace: RenderTrace) -> ShadowNode:
    return node._copy(trace=trace)


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
        trace = RenderTrace()

        def on_yielded_for(base_trace: RenderTrace):
            i = 1

            def on_yielded(
                node: Component[X] | X | Iterable[X] | Iterable[Component[X]],
            ):
                if isinstance(node, Iterable):
                    for n in node:
                        on_yielded(n)
                    return

                node_type = self._reconciler.node_type
                nonlocal rendering, i
                my_trace = base_trace + RenderFrame(
                    pos=i, type=node.__class__, key=node.key
                )

                i += 1
                if isinstance(node, node_type):  # type: ignore
                    rendering += (with_trace(node, my_trace),)
                elif isinstance(node, Component):
                    node.render(on_yielded_for(my_trace), self.context)
                else:
                    raise TypeError(
                        f"Expected render method to return {node_type} or Component, but got {type(node)}"
                    )

            return on_yielded

        yield_ = on_yielded_for(trace)
        yield_(self._mounted)
        return rendering

    def remount(self, root: Component[X]):
        self._mounted = root
        self.force_rerender()

    def force_rerender(self):
        self._reconciler.reconcile(self._compute_render())
