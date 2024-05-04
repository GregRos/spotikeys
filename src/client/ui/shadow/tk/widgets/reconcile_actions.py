from dataclasses import dataclass, field
from itertools import zip_longest


from tkinter import Label, Tk, Widget
from typing import TYPE_CHECKING, Any, Callable, Generator, Literal, final, override


from src.client.ui.framework.make_clickthrough import make_clickthrough
from src.client.ui.shadow.core.reconciler.actions import (
    ReconcileActions,
    ResourceRecord,
)
from src.client.ui.shadow.core.props.shadow_node import ShadowNode
from src.client.ui.shadow.tk.widgets.widget import SwTkWidget


type TkWidgetRecord = ResourceRecord[SwTkWidget, Widget]


@final
@dataclass
class TkWidgetActions(ReconcileActions[SwTkWidget, Widget]):
    tk: Tk

    @override
    def create(self, node: SwTkWidget):
        match node.tk_type:
            case "Label":
                return Label(self.tk, **node._props.compute("configure"))
            case _:
                raise ValueError(f"Unknown type: {node.tk_type}")

    @override
    def destroy(self, existing: TkWidgetRecord):
        existing.resource.destroy()

    @override
    def replace(self, existing: TkWidgetRecord, next: TkWidgetRecord):
        pack_info = next.node._props.compute("pack")
        next.resource.pack_configure(after=existing.resource, **pack_info)
        existing.resource.pack_forget()
        make_clickthrough(next.resource)
    @override
    def place(self, record: TkWidgetRecord):
        pack_info = record.node._props.compute("pack")
        record.resource.pack_configure(**pack_info)
        make_clickthrough(record.resource)

    @override
    def unplace(self, existing: TkWidgetRecord):
        existing.resource.pack_forget()

    @override
    def update(self, existing: TkWidgetRecord, next: SwTkWidget):
        updates = existing.node._props.diff(next._props).compute()
        existing.resource.configure(**updates["configure"])
