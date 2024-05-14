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


from src.client.ui.shadow.model.props.operators import compute
from src.client.ui.shadow.model.props.dict.props_dict import PropsDict
from src.client.ui.shadow.model.components.component import Component
from src.client.ui.shadow.model.nodes.resource import (
    Compat,
    ShadowedResource,
)
from src.client.ui.shadow.model.nodes.shadow_node import ShadowProps
from src.client.ui.shadow.core.stateful_reconciler import StatefulReconciler
from src.client.ui.shadow.core.renderer import ComponentMount
from src.client.ui.shadow.core.context import Ctx
from src.client.ui.shadow.tk.widgets.component_mount import WidgetComponentMount
from src.client.ui.shadow.tk.widgets.widget import WidgetNode
from src.client.ui.shadow.tk.widgets.widget_wrapper import WidgetWrapper
from src.client.ui.shadow.tk.window.window import SwTkWindow
from src.client.ui.values.geometry import Geometry


class TkWrapper(ShadowedResource[SwTkWindow]):
    resource: Tk
    _component_mount: WidgetComponentMount

    @staticmethod
    @override
    def node_type() -> type[SwTkWindow]:
        return SwTkWindow

    def __init__(self, node: SwTkWindow, resource: Tk, context: Ctx):
        super().__init__(node)
        self.resource = resource
        self.context = context
        self._component_mount = WidgetComponentMount(resource, context)

    @override
    def is_same_resource(self, other: Self) -> bool:
        return self.resource is other.resource

    @staticmethod
    def create(node: SwTkWindow, context: Ctx) -> "TkWrapper":
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

        wrapper = TkWrapper(node, tk, context)
        return wrapper

    def schedule(
        self,
        action: Callable[[], Any],
    ):
        self.resource.after(0, action)

    @override
    def migrate(self, node: SwTkWindow) -> Self:
        return self.__class__(node, self.resource, self.context)

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
            geo = self.props()["geometry"].normalize(self.resource).to_tk()
            self.resource.wm_geometry(geo)
            self.resource.deiconify()

        self.schedule(do)

    @override
    def get_compatibility(self, other: SwTkWindow) -> Compat:
        return "update"

    @override
    def update(self, props: PropsDict) -> None:
        x = compute("", props)
        if not x:
            return
        _, computed = x
        assert isinstance(computed, dict)

        def do():
            if attrs := computed["attributes"]:
                attributes = [
                    item for k, v in attrs.items() for item in (f"-{k}", v) if v
                ]
                self.resource.attributes(*attributes)
            if configure := computed["configure"]:
                self.resource.configure(**configure)
            if ("", "override_redirect") in computed:
                self.resource.overrideredirect(computed["", "override_redirect"])
            if children := computed["children"]:
                self._component_mount.mount(Component(key="WidgetRoot")[*children])

        self.schedule(do)
