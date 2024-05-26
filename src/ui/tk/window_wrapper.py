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


from src.ui.model.prop_dict import PValues, PDict
from src.ui.model.component import Component
from src.ui.model.resource import (
    Compat,
    ShadowedResource,
)
from src.ui.model.shadow_node import ShadowProps
from src.ui.rendering.stateful_reconciler import StatefulReconciler
from src.ui.rendering.renderer import ComponentMount
from src.ui.model.context import Ctx
from src.ui.tk.make_clickthrough import make_clickthrough
from src.ui.tk.widget_mount import WidgetMount
from src.ui.tk.widget import Widget
from src.ui.tk.widget_wrapper import WidgetWrapper
from src.ui.tk.window import Window
from src.ui.tk.geometry import Geometry


class WindowWrapper(ShadowedResource[Window]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    resource: Tk
    _component_mount: WidgetMount

    @staticmethod
    @override
    def node_type() -> type[Window]:
        return Window

    def __init__(self, node: Window, resource: Tk, context: Ctx, root: Component):
        super().__init__(node)
        self.resource = resource
        self.context = context
        self._component_mount = WidgetMount(resource, context, root)

    @override
    def is_same_resource(self, other: Self) -> bool:
        return self.resource is other.resource

    @staticmethod
    def create(node: Window, context: Ctx) -> "WindowWrapper":
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

        wrapper = WindowWrapper(node, tk, context, root=root)
        return wrapper

    def schedule(
        self,
        action: Callable[[], Any],
    ):
        self.resource.after(0, action)

    @override
    def migrate(self, node: Window) -> Self:
        return self.__class__(
            node, self.resource, self.context, self._component_mount._mounted
        )

    @override
    def destroy(self) -> None:
        self.schedule(self.resource.destroy)

    @override
    def replace(self, other: "WindowWrapper") -> None:
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
            geo = self.node._props["Geometry"].value
            geo = self.normalize_geo(geo)
            self.resource.wm_geometry(geo)
            self.resource.deiconify()

        self.schedule(do)

    @override
    def get_compatibility(self, other: Window) -> Compat:
        return "update"

    @override
    def update(self, props: PValues) -> None:
        x = props.compute()
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
            if "override_redirect" in computed:
                self.resource.overrideredirect(computed["override_redirect"])
            if children := self.node.children:
                self._component_mount.remount(children)

        self.schedule(do)
