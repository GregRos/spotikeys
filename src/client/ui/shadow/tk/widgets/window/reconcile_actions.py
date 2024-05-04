from dataclasses import dataclass, field
from itertools import zip_longest


import threading
from tkinter import Label, Tk, Widget
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generator,
    Literal,
    Self,
    final,
    override,
)

import attr
from pyrsistent import PMap, PRecord


from src.client.ui.framework.component import Component, ContainerComponent
from src.client.ui.shadow.core.props.props_map import PropsMap
from src.client.ui.shadow.core.reconciler.actions import (
    Compat,
    ShadowedResource,
)
from src.client.ui.shadow.core.props.shadow_node import ShadowNode
from src.client.ui.shadow.core.reconciler.stateful_reconciler import StatefulReconciler
from src.client.ui.shadow.tk.widgets.widget import SwTkWidget
from src.client.ui.shadow.tk.widgets.widget_wrapper import WidgetWrapper
from src.client.ui.shadow.tk.window.window import SwTkWindow
from src.client.ui.values.geometry import Geometry


class TkWrapper(ShadowedResource[SwTkWindow]):
    resource: Tk
    _render_state: StatefulReconciler

    def __init__(self, node: SwTkWindow, resource: Tk):
        super().__init__(node)
        self.resource = resource
        self._render_state = StatefulReconciler(
            lambda x: WidgetWrapper.create(resource, x)
        )

    @override
    def is_same_resource(self, other: Self) -> bool:
        return self.resource is other.resource

    @staticmethod
    def create(node: SwTkWindow) -> "TkWrapper":
        waiter = threading.Event()
        tk: Tk = None  # type: ignore

        def ui_thread():
            nonlocal tk
            tk = Tk()
            waiter.set()
            tk.mainloop()

        thread = threading.Thread(target=ui_thread)
        thread.start()
        waiter.wait()

        wrapper = TkWrapper(node, tk)
        return wrapper

    def schedule(
        self,
        action: Callable[[], Any],
    ):
        self.resource.after(0, action)

    @override
    def migrate(self, node: SwTkWindow) -> Self:
        return self.__class__(node, self.resource)

    @override
    def destroy(self) -> None:
        self.schedule(self.resource.destroy)

    @override
    def replace(self, other: "TkWrapper") -> None:
        self.resource.withdraw()
        other.resource.deiconify()

    @override
    def unplace(self) -> None:
        self.resource.withdraw()

    @override
    def place(self) -> None:
        self.resource.wm_geometry(self.node.geometry.to_tk())
        self.resource.deiconify()

    @override
    def get_compatibility(self, other: SwTkWindow) -> Compat:
        return "update"

    @override
    def update(self, props: PropsMap) -> None:
        diff = props.compute()
        if attrs := diff.attributes:
            attributes = [item for k, v in attrs.items() for item in (f"-{k}", v) if v]
            self.resource.attributes(*attributes)
        if geometry := diff.geometry:
            self.resource.geometry(Geometry(**geometry).to_tk())
        if special := diff.special:
            self.resource.overrideredirect(special.override_redirect)
        if configure := diff.configure:
            self.resource.configure(**configure)
        self._render_state.mount(
            ContainerComponent(
                key="root",
                children=self.node.children,
            )
        )
