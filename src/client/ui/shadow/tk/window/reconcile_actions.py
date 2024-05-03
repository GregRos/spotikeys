from dataclasses import dataclass, field
from itertools import zip_longest


from tkinter import Label, Tk, Widget
from typing import TYPE_CHECKING, Any, Callable, Generator, Literal, final, override

import attr


from src.client.ui.shadow.core.reconciler.actions import (
    ReconcileActions,
    ResourceRecord,
)
from src.client.ui.shadow.core.props.shadow_node import ShadowNode
from src.client.ui.shadow.tk.widgets.widget import SwTkWidget
from src.client.ui.shadow.tk.window.window import SwTkWindow


type TkRecord = ResourceRecord[SwTkWindow, Tk]


@final
@dataclass
class TkWindowActions(ReconcileActions[SwTkWindow, Tk]):
    tk: Tk

    @override
    def create(self, node: SwTkWindow):
        return Tk()

    @override
    def destroy(self, existing: TkRecord):
        existing.resource.destroy()

    @override
    def replace(self, existing: TkRecord, next: TkRecord):
        self.unplace(existing)
        next.resource.deiconify()

    @override
    def unplace(self, existing: TkRecord):
        existing.resource.withdraw()

    @override
    def update(self, existing: TkRecord, next: SwTkWindow):
        attributes = next._props.attributes.diff(existing.node._props.attributes)
        attributes_args = [item for k, v in attributes for item in (f"-{k}", v)]
        if attributes_args:
            existing.resource.attributes(*attributes_args)
        if next._props.geometry != existing.node._props.geometry:
            existing.resource.geometry(
                next.geometry.normalize(existing.resource).to_tk()
            )
        if (
            next._props.special["override_redirect"]
            != existing.node._props.special["override_redirect"]
        ):
            existing.resource.overrideredirect(next.override_redirect)
