from dataclasses import field
from itertools import zip_longest


from tkinter import Widget
from typing import TYPE_CHECKING, Any, Callable, Generator

from src.client.ui.shadow.core.base import Mismatch, ShadowNode
from src.client.ui.shadow.core.reconciler.property_dict import (
    compute_diff,
    compute_values,
)


class Reconcile:
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

        if any_reconcile or force_place:
            target.update_idletasks()
            self.post_reconcile(target) if self.post_reconcile else None
