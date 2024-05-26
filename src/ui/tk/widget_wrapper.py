from tkinter import Label, Tk, Widget as TkWidget
from typing import Any, ClassVar, Self, final, override
from src.ui.model.prop_dict import PValues, PDict
from src.ui.tk.make_clickthrough import make_clickthrough
from src.ui.model.resource import Compat, ShadowedResource
from src.ui.tk.widget import Widget


class WidgetWrapper(ShadowedResource[Widget]):

    @staticmethod
    @override
    def node_type() -> type[Widget]:
        return Widget

    @final
    @override
    def migrate(self, node: Widget) -> Self:
        x = WidgetWrapper(node, self.resource)
        return x  # type: ignore

    @staticmethod
    def create(tk: Tk, node: Widget) -> "WidgetWrapper":
        match node.type_name:
            case "Label":
                return __class__(node, Label(tk))
            case _:
                raise ValueError(f"Unknown type: {node.type_name}")

    @override
    def get_compatibility(self, other: Widget) -> Compat:
        if self.node.type_name != other.type_name:
            return "recreate"
        elif self.node._props["pack"] != other._props["pack"]:
            return "replace"
        else:
            return "update"

    def __init__(self, node: Widget, resource: TkWidget) -> None:
        super().__init__(node)
        self.resource = resource

    @staticmethod
    def _wrap(node: Widget, resource: TkWidget) -> "WidgetWrapper":
        return WidgetWrapper(node, resource)

    @override
    def is_same_resource(self, other: Self) -> bool:
        return self.resource == other.resource

    @override
    def destroy(self) -> None:
        self.resource.destroy()

    @override
    def update(self, props: PValues) -> None:
        _, diff = props.compute()
        self.resource.configure(**diff.get("configure", {}))

    @override
    def place(self) -> None:
        _, d = self.node._props.compute()

        self.resource.pack_configure(**d.get("pack", {}))
        make_clickthrough(self.resource)

    @override
    def unplace(self) -> None:
        self.resource.pack_forget()

    @override
    def replace(self, other: Self) -> None:
        _, p = other.node._props.compute()

        other.resource.pack_configure(after=self.resource, **p.get("pack", {}))

        self.resource.pack_forget()
        make_clickthrough(other.resource)
