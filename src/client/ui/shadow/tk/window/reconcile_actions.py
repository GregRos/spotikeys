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
        self.schedule(self.resource.deiconify)
        other.unplace()

    @override
    def unplace(self) -> None:
        self.schedule(self.resource.withdraw)

    @override
    def place(self) -> None:
        def do():
            geo = self.node.geometry.normalize(self.resource).to_tk()
            self.resource.wm_geometry(geo)
            self.resource.deiconify()

        self.schedule(do)

    @override
    def get_compatibility(self, other: SwTkWindow) -> Compat:
        return "update"

    @override
    def update(self, props: PropsMap) -> None:
        diff = props.compute()

        def do():
            if (attrs := diff.attributes) is not None:
                attributes = [
                    item for k, v in attrs.items() for item in (f"-{k}", v) if v
                ]
                self.resource.attributes(*attributes)
            if (configure := diff.configure) is not None:
                self.resource.configure(**configure)

            if (special := diff.get("special")) is not None:
                if (override_redirect := special.get("override_redirect")) is not None:
                    self.resource.overrideredirect(override_redirect)
                if children := special.get("children"):
                    self._render_state.mount(
                        ContainerComponent(
                            key="root",
                            children=children,
                        )
                    )

        self.schedule(do)
