from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from itertools import zip_longest


import threading
from tkinter import Label, Tk, Widget
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Generator,
    Literal,
    Mapping,
    Self,
    final,
    override,
)


from src.client.ui.shadow.model.props.dict.props_dict import PropVals, PropsDict
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
    model_config = ConfigDict(arbitrary_types_allowed=True)
    resource: Tk
    _component_mount: WidgetComponentMount

    @staticmethod
    @override
    def node_type() -> type[SwTkWindow]:
        return SwTkWindow

    def __init__(self, node: SwTkWindow, resource: Tk, context: Ctx, root: Component):
        super().__init__(node)
        self.resource = resource
        self.context = context
        self._component_mount = WidgetComponentMount(resource, context, root)

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
        root = Component(key="WidgetRoot")[*node.children]

        wrapper = TkWrapper(node, tk, context, root=root)
        return wrapper

    def schedule(
        self,
        action: Callable[[], Any],
    ):
        self.resource.after(0, action)

    @override
    def migrate(self, node: SwTkWindow) -> Self:
        return self.__class__(
            node, self.resource, self.context, self._component_mount._mounted
        )

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

    def normalize_geo(self, geo: Mapping[str, Any]) -> str:
        x, y, width, height = (geo[k] for k in ("x", "y", "width", "height"))
        if x < 0:
            x = self.resource.winfo_screenwidth() + x
        if y < 0:
            y = self.resource.winfo_screenheight() + y
        return f"{width}x{height}+{x}+{y}"

    @override
    def place(self) -> None:
        def do():
            geo = self.node._props["geometry"].value
            geo = self.normalize_geo(geo)
            self.resource.wm_geometry(geo)
            self.resource.deiconify()

        self.schedule(do)

    @override
    def get_compatibility(self, other: SwTkWindow) -> Compat:
        return "update"

    @override
    def update(self, props: PropVals) -> None:
        x = props.compute("")
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
                self.resource.overrideredirect(computed["override_redirect"])
            if children := self.node.children:
                self._component_mount.remount(children)

        self.schedule(do)
