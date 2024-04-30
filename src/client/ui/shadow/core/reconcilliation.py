from dataclasses import field
from itertools import zip_longest
from attr import dataclass


from tkinter import Label, Tk, Widget
from typing import TYPE_CHECKING, Any, Callable, Generator

from src.client.ui.shadow.core.base import Mismatch, ShadowNode
from src.client.ui.shadow.core.property_dict import compute_diff, compute_values

if TYPE_CHECKING:
    from src.client.ui.framework.component import Component


class Unplace:
    def __init__(self, prev: ShadowNode):
        self.prev = prev

    @property
    def key(self) -> str:
        return self.prev.key

    @property
    def tk_type(self) -> str:
        return self.prev.tk_type


class Reconciliation:
    @property
    def key(self) -> str:
        return self.next.key

    @property
    def tk_type(self) -> str:
        return self.next.tk_type

    def __init__(self, prev: "ShadowNode | None", next: ShadowNode):
        self.prev = prev
        self.next = next

        prev_dict = prev.to_property_dict() if not self.mismatch and prev else {}
        next_dict = next.to_property_dict() if next else {}
        diff = compute_diff(prev_dict, next_dict)
        values = compute_values(diff)
        self.configure = values["configure"]
        self.place = values["place"]
        self.post_reconcile = next.post_reconcile

    @property
    def mismatch(self) -> Mismatch:
        prev, next = self.prev, self.next
        if not next:
            return "unnecessary"
        if not prev:
            return "missing"
        if prev.key != next.key:
            return "different_key"
        if prev.tk_type != next.tk_type:
            return "same_key_different_type"
        return None

    def __bool__(self):
        return bool(self.configure or self.place or self.mismatch)

    def __call__(self, target: Widget, force_place: bool = False):
        assert target.widgetName == self.tk_type
        any_reconcile = False
        if self.configure:
            target.configure(**self.configure)
            any_reconcile = True
        if self.place or force_place:
            target.place(**self.place)
            any_reconcile = True

        if any_reconcile:

            target.update_idletasks()


@dataclass
class StatefulReconciler:
    _tk: Tk
    _rendering: dict[ShadowNode, Widget]
    _ordering: list[ShadowNode[Widget]]
    _key_to_widget: dict[str, Widget]
    _bin: dict[ShadowNode, Widget]

    def create_widget(self, w_type: str):
        match w_type:
            case "Label":
                return Label(self._tk)
            case _:
                raise ValueError(f"Unknown tk_type {w_type}")

    def find_reconcile_target(self, reconciliation: Reconciliation) -> Widget:

        if reconciliation.mismatch == "different_key":
            # This means the key is different. We're going to try to find a Widget
            # with the same key and reconcile on it.
            return self._key_to_widget.get(
                reconciliation.key, None
            ) or self.create_widget(reconciliation.tk_type)
            # If we don't find it, it will be created.
        elif reconciliation.mismatch == "same_key_different_type":
            # This a problem. We can't reconcile different types of widgets.
            prev: ShadowNode = reconciliation.prev  # type: ignore
            target = self._key_to_widget[prev.key]
            target.destroy()
            return self.create_widget(reconciliation.tk_type)
        elif reconciliation.mismatch == "missing":
            return self.create_widget(reconciliation.tk_type)
        else:
            return self._key_to_widget[reconciliation.key]

    def reconcile(self, root: "Component"):
        from src.client.ui.framework.component import Component

        def render_recursively(
            component: Component,
        ) -> Generator[ShadowNode[Widget], None, None]:
            for child in component.render():
                if isinstance(child, Component):
                    yield from render_recursively(child)
                else:
                    yield child

        rendering = list(render_recursively(root))

        reconciliations = [
            Reconciliation(x, y)
            for x, y in zip_longest(rendering, self._ordering, fillvalue=None)
        ]
        i = 0
        start_force_placing = -1
        while i < min(len(self._ordering), len(rendering)):
            prev_node = self._ordering[i]
            current_node = rendering[i]
            reconciliation = prev_node.__class__.reconcile(prev_node, current_node)

            rendered_node = rendering[i]
            if prev_node != rendered_node:
                reconciliations.append(
                    prev_node.__class__.reconcile(
                        self._rendering[prev_node], rendered_node
                    )
                )
            if self._ordering[i] != rendering[j]:
                reconciliations.append(
                    Reconciliation(
                        rendering[j].key,
                        rendering[j].tk_type,
                        rendering[j].to_property_dict(),
                        {},
                        post_reconcile=root[j].post_reconcile,
                    )
                )
            else:
                reconciliations.append(
                    ShadowNode.reconcile(self._rendering[self._ordering[i]], root[j])
                )
            i += 1
            j += 1
        for child in render_recursively(root):
            if child not in self._ordering:
                self._rendering[child] = None
            reconciliations.append(ShadowNode.reconcile(self._rendering[child], child))

        for node, widget in self._rendering.items():
            if not widget:
                widget = self.create_widget(node.tk_type)
                self._rendering[node] = widget
            rec = node.reconcile(widget)
            rec(widget)
        self._tk.update_idletasks()
        return self._rendering
