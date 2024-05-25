from tkinter import Label, Tk, Widget
from typing import Any, ClassVar, Self, final, override
from src.client.ui.shadow.model.props.operators import compute
from src.client.ui.shadow.model.props.dict.props_dict import PropVals, PropsDict
from src.client.ui.shadow.tk.make_clickthrough import make_clickthrough
from src.client.ui.shadow.model.nodes.resource import Compat, ShadowedResource
from src.client.ui.shadow.tk.widgets.widget import WidgetNode


class WidgetWrapper(ShadowedResource[WidgetNode]):

    @staticmethod
    @override
    def node_type() -> type[WidgetNode]:
        return WidgetNode

    @final
    @override
    def migrate(self, node: WidgetNode) -> Self:
        x = WidgetWrapper(node, self.resource)
        return x  # type: ignore

    @staticmethod
    def create(tk: Tk, node: WidgetNode) -> "WidgetWrapper":
        match node.__class__.tk_type:
            case "Label":
                return __class__(node, Label(tk))
            case _:
                raise ValueError(f"Unknown type: {node.tk_type}")

    @override
    def get_compatibility(self, other: WidgetNode) -> Compat:
        if self.node.tk_type != other.tk_type:
            return "recreate"
        elif self.node._props["pack"] != other._props["pack"]:
            return "replace"
        else:
            return "update"

    def __init__(self, node: WidgetNode, resource: Widget) -> None:
        super().__init__(node)
        self.resource = resource

    @staticmethod
    def _wrap(node: WidgetNode, resource: Widget) -> "WidgetWrapper":
        return WidgetWrapper(node, resource)

    @override
    def is_same_resource(self, other: Self) -> bool:
        return self.resource == other.resource

    @override
    def destroy(self) -> None:
        self.resource.destroy()

    @override
    def update(self, props: PropVals) -> None:
        _, diff = compute("", props["configure"]) or {}
        self.resource.configure(**diff)

    @override
    def place(self) -> None:
        _, d = compute("", self.node._props["pack"]) or {}

        self.resource.pack_configure(**d["pack"])
        make_clickthrough(self.resource)

    @override
    def unplace(self) -> None:
        self.resource.pack_forget()

    @override
    def replace(self, other: Self) -> None:
        p = compute("", other.node._props["pack"])
        assert p
        _, computed = p
        other.resource.pack_configure(after=self.resource, **computed)

        self.resource.pack_forget()
        make_clickthrough(other.resource)
