from dataclasses import dataclass
from src.client.ui.framework.component import Component
from src.client.ui.shadow.core.base import ShadowNode
from src.client.ui.shadow.core.reconciler.reconcile import Reconcile


from itertools import groupby, zip_longest
from tkinter import Label, Tk, Widget

from src.client.ui.shadow.core.reconciler.unplace import Unplace


@dataclass
class StatefulReconciler:
    _tk: Tk
    _ordering: list[ShadowNode[Widget]]
    _key_to_widget: dict[str, Widget]

    def create_widget(self, w_type: str, key: str):
        match w_type:
            case "Label":
                return Label(self._tk, name=key)
            case _:
                raise ValueError(f"Unknown tk_type {w_type}")

    def when_unrendered(self, key: str):
        target = self._key_to_widget[key]
        target.pack_forget()

    def when_needs_creation(self, key: str, tk_type: str):
        target = self.create_widget(tk_type, key)
        self._key_to_widget[key] = target
        return target

    def when_needs_recreation(self, existing: Widget, tk_type: str, key: str):
        existing.destroy()

        return self.when_needs_creation(key, tk_type)

    def reconcile_action(self, reconcile: Reconcile | Unplace) -> None:
        if isinstance(reconcile, Unplace):
            return self.when_unrendered(reconcile.key)

        if reconcile.mismatch == "different_key":
            # This means the key is different. We're going to try to find a Widget
            # with the same key and reconcile on it.
            existing = self._key_to_widget.get(reconcile.key)
            if existing:
                # Means a widget with this key and the same type already exists but
                # was placed elsewhere. We'll reuse it.
                target = existing
            else:
                target = self.when_needs_creation(reconcile.key, reconcile.tk_type)
            # If we don't find it, it will be created.
        elif reconcile.mismatch == "same_key_different_type":
            # This a problem. We can't reconcile different types of widgets.
            prev: ShadowNode = reconcile.prev  # type: ignore
            target = self.when_needs_recreation(
                self._key_to_widget[reconcile.key], reconcile.tk_type, reconcile.key
            )
        elif reconcile.mismatch == "missing":
            target = self.when_needs_creation(reconcile.key, reconcile.tk_type)
        else:
            target = self._key_to_widget[reconcile.key]

        reconcile(target)

    def check_duplicates(self, rendering: list[ShadowNode[Widget]]):
        key_to_nodes = {
            key: list(group) for key, group in groupby(rendering, key=lambda x: x.key)
        }
        messages = {
            key: f"Duplicates for {key} found: {group} "
            for key, group in key_to_nodes
            if len(group) > 1
        }
        if messages:
            raise ValueError(messages)

    def compute_reconcile(self, rendering: list[ShadowNode[Widget]]):
        self.check_duplicates(rendering)
        placed = dict()
        for prev, next in zip_longest(self._ordering, rendering, fillvalue=None):
            if not next:
                assert prev
                if prev.key in placed:
                    # this widget was moved around and has been placed again
                    continue
                # Means this widget should be removed
                yield Unplace(prev)
                continue
            # Widgets at the same index must be reconciled
            # prev could be None here
            reconcile = Reconcile(prev, next)
            # this also handles the case where the widget type changes
            # but the key remains the same
            placed[next.key] = next
            yield reconcile

    def render_recursively(self, component: "Component"):
        for child in component.render():
            if isinstance(child, "Component"):
                yield from self.render_recursively(child)
            else:
                yield child

    def reconcile(self, root: "Component"):
        from src.client.ui.framework.component import Component

        rendering = list(self.render_recursively(root))
        reconcile = [*self.compute_reconcile(rendering)]
        for reconcile in reconcile:
            self.reconcile_action(reconcile)
