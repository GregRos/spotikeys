from dataclasses import dataclass, field
from itertools import zip_longest


from tkinter import Label, Tk, Widget
from typing import TYPE_CHECKING, Any, Callable, Generator, Literal, final, override


from src.client.ui.shadow.core.base import Mismatch, ShadowNode, ShadowTkWidget

from src.client.ui.shadow.core.reconciler.property_dict import PropertyDict
from src.client.ui.shadow.core.reconciler.stateful_reconciler import (
    ResourceActions,
    ResourceRecord,
)


type TkWidgetRecord = ResourceRecord[ShadowTkWidget, Widget]


@final
@dataclass
class TkWidgetActions(ResourceActions[ShadowTkWidget, Widget]):
    tk: Tk

    @override
    def create(self, node: ShadowTkWidget):
        match node:
            case "Label":
                return Label(self.tk, text=node.key)
            case _:
                raise ValueError(f"Unknown type: {node.tk_type}")

    @override
    def destroy(self, existing: TkWidgetRecord):
        existing.resource.destroy()

    @override
    def replace(self, existing: TkWidgetRecord, next: TkWidgetRecord):
        pack_info = next.node._diff(None).compute()["pack"]
        next.resource.pack_configure(after=existing.resource, **pack_info)
        existing.resource.pack_forget()

    @override
    def unplace(self, existing: TkWidgetRecord):
        existing.resource.pack_forget()

    @override
    def update(self, existing: TkWidgetRecord, next: ShadowTkWidget):
        updates = next._diff(existing.node).compute()
        existing.resource.configure(**updates["configure"])

    @override
    def get_compatibility(
        self, prev: ShadowTkWidget, next: ShadowTkWidget
    ) -> Literal["update"] | Literal["replace"] | Literal["recreate"]:
        if prev.tk_type != next.tk_type:
            return "recreate"
        if prev._props
        return "update"
