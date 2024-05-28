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
    Resource,
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


class WindowWrapper(Resource[Window]):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    resource: Tk
    _component_mount: WidgetMount

    @staticmethod
    @override
    def node_type() -> type[Window]:
        return Window

    def __init__(
        self,
        node: Window,
        resource: Tk,
        context: Ctx,
        root: Component,
        mount: WidgetMount | None = None,
    ):
        super().__init__(node)
        mount = mount or WidgetMount(resource, context, root)
        self.resource = resource
        self.context = context
        self._component_mount = mount

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
        root = node._props.compute()[1]["child"]  # type: Any

        wrapper = WindowWrapper(node, tk, context, root=root)

        return wrapper

    def run_in_owner(
        self,
        action: Callable[[], Any],
    ):
        if threading.current_thread().name == "ui_thread":
            action()
            return
        e = threading.Event()
        err = None  # type: Any

        def wrap_action():
            nonlocal err
            try:
                action()
            except Exception as ex:
                err = ex
            finally:
                e.set()

        self.resource.after(0, wrap_action)
        e.wait()
        if err:
            raise Exception("Error during scheduled action") from err

    @override
    def migrate(self, node: Window) -> Self:
        return self.__class__(
            node,
            self.resource,
            self.context,
            self._component_mount._mounted,
            self._component_mount,
        )

    @override
    def destroy(self) -> None:
        self.run_in_owner(self.resource.destroy)

    @override
    def replace(self, other: "WindowWrapper") -> None:
        def do_replace():

            self.resource.withdraw()
            other.place()
            other.resource.deiconify()

        self.run_in_owner(do_replace)

    @override
    def unplace(self) -> None:
        self.run_in_owner(self.resource.withdraw)

    def normalize_geo(self, geo: Geometry) -> str:
        x, y, width, height = (geo[k] for k in ("x", "y", "width", "height"))
        if x < 0:
            x = self.resource.winfo_screenwidth() + x
        if y < 0:
            y = self.resource.winfo_screenheight() + y
        match geo["anchor_point"]:
            case "lt":
                pass
            case "rt":
                x -= width
            case "lb":
                y -= height
            case "rb":
                x -= width
                y -= height

        return f"{width}x{height}+{x}+{y}"

    @override
    def place(self) -> None:
        def do():
            geo = self.node._props["Geometry"].value  # type: Geometry # type: ignore
            normed = self.normalize_geo(geo)
            print(f"Setting {self.key} geometry to {normed}")
            self.resource.wm_geometry(normed)
            self.resource.deiconify()

        self.run_in_owner(do)

    @override
    def get_compatibility(self, other: Window) -> Compat:
        return "update"

    @override
    def update(self, props: PValues) -> None:
        x = props.compute()
        _, computed = x
        assert isinstance(computed, dict)

        def do():
            if attrs := computed.get("attributes"):
                attributes = [
                    item for k, v in attrs.items() for item in (f"-{k}", v) if v
                ]
                self.resource.attributes(*attributes)
            if configure := computed.get("configure"):
                self.resource.configure(**configure)
            if (override_redirect := computed.get("override_redirect")) is not None:
                self.resource.overrideredirect(override_redirect)
            if child := computed.get("child"):
                self._component_mount.remount(child)

        self.run_in_owner(do)
