from dataclasses import dataclass, field
from itertools import zip_longest


import threading
from tkinter import Label, Tk, Widget
from typing import TYPE_CHECKING, Any, Callable, Generator, Literal, final, override

import attr
from pyrsistent import PMap, PRecord


from src.client.ui.framework.component import Component
from src.client.ui.shadow.core.props.props_map import PropsMap
from src.client.ui.shadow.core.reconciler.actions import (
    ReconcileActions,
    ResourceRecord,
)
from src.client.ui.shadow.core.props.shadow_node import ShadowNode
from src.client.ui.shadow.core.reconciler.stateful_reconciler import StatefulReconciler
from src.client.ui.shadow.tk.widgets.reconcile_actions import TkWidgetActions
from src.client.ui.shadow.tk.widgets.widget import SwTkWidget
from src.client.ui.shadow.tk.window.window import SwTkWindow
from src.client.ui.values.geometry import Geometry


class TkWrapper:
    _render_state: StatefulReconciler[SwTkWidget, Widget]
    tk: Tk

    def __init__(self):
        waiter = threading.Event()
        tk: Tk

        def ui_thread():
            self.tk = Tk()
            waiter.set()
            self.tk.mainloop()

        thread = threading.Thread(target=ui_thread)
        thread.start()
        waiter.wait()
        self._render_state = StatefulReconciler(TkWidgetActions(self.tk))
        # type: ignore

    def schedule(
        self,
        action: Callable[[], Any],
    ):
        self.tk.after(0, action)

    def destroy(self):
        self.schedule(self.tk.destroy)

    def deiconify(self):
        self.schedule(self.tk.deiconify)

    def withdraw(self):
        self.schedule(self.tk.withdraw)

    def update_children(self, root: Component[SwTkWidget]):
        self.schedule(lambda: self._render_state.reconcile(root))

    def update(self, properties: PMap[str, PMap[str, Any]]):
        def do_update():
            if attrs := properties.get("attributes"):
                attributes = [
                    item for k, v in attrs.items() for item in (f"-{k}", v) if v
                ]
                self.tk.attributes(*attributes)
            if geometry := properties.get("geometry"):
                self.tk.geometry(Geometry(**geometry).to_tk())
            if special := properties.get("special"):
                self.tk.overrideredirect(special.override_redirect)
            if configure := properties.get("configure"):
                self.tk.configure(**configure)

        self.schedule(do_update)


type TkRecord = ResourceRecord[SwTkWindow, TkWrapper]


@final
@dataclass
class TkWindowActions(ReconcileActions[SwTkWindow, TkWrapper]):
    @override
    def create(self, node: SwTkWindow):
        wrapper = TkWrapper()
        wrapper.update(node._props.compute())
        wrapper.update_children(node.root)
        return wrapper

    @override
    def destroy(self, existing: TkRecord):
        existing.resource.destroy()

    @override
    def replace(self, existing: TkRecord, next: TkRecord):
        existing.resource.withdraw()
        next.resource.deiconify()

    @override
    def unplace(self, existing: TkRecord):
        existing.resource.withdraw()

    @override
    def update(self, existing: TkRecord, next: SwTkWindow):
        diff = existing.node._props.diff(next._props).compute()
        existing.resource.update(diff)
        existing.resource.update_children(next.root)
