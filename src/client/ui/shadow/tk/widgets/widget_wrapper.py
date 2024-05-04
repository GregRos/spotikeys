from tkinter import Label, Tk, Widget
from typing import Any, ClassVar, Self, final, override
from src.client.ui.framework.make_clickthrough import make_clickthrough
from src.client.ui.shadow.core.props.props_map import PropsMap
from src.client.ui.shadow.core.reconciler.actions import Compat, ShadowedResource
from src.client.ui.shadow.tk.widgets.widget import SwTkWidget


class WidgetWrapper(ShadowedResource[SwTkWidget]):
    @final
    @override
    def migrate(self, node: SwTkWidget) -> Self:
        x = WidgetWrapper(node, self.resource)
        return x  # type: ignore

    @staticmethod
    def create(tk: Tk, node: SwTkWidget) -> "WidgetWrapper":
        match node.tk_type:
            case "Label":
                return __class__(node, Label(tk, **node._props.compute("configure")))
            case _:
                raise ValueError(f"Unknown type: {node.tk_type}")

    @override
    def get_compatibility(self, other: SwTkWidget) -> Compat:
        if self.node.tk_type != other.tk_type:
            return "recreate"
        elif self.node._props.pack != other._props.pack:
            return "replace"
        else:
            return "update"

    def __init__(self, node: SwTkWidget, resource: Widget) -> None:
        super().__init__(node)
        self.resource = resource

    @staticmethod
    def _wrap(node: SwTkWidget, resource: Widget) -> "WidgetWrapper":
        return WidgetWrapper(node, resource)

    @override
    def is_same_resource(self, other: Self) -> bool:
        return self.resource == other.resource

    @override
    def destroy(self) -> None:
        self.resource.destroy()

    @override
    def update(self, props: PropsMap) -> None:
        diff = props.compute("configure")
        self.resource.configure(**diff)

    @override
    def place(self) -> None:
        self.resource.pack_configure(**self.node._props.compute("pack"))
        make_clickthrough(self.resource)

    @override
    def unplace(self) -> None:
        self.resource.pack_forget()

    @override
    def replace(self, other: Self) -> None:
        other.resource.pack_configure(
            after=self.resource, **other.node._props.compute("pack")
        )
        self.resource.pack_forget()
        make_clickthrough(other.resource)
