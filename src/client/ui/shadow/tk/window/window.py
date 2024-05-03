from dataclasses import dataclass, field
from tkinter import Tk
from typing import Literal, override

from src.client.ui.framework.make_clickthrough import make_clickthrough
from src.client.ui.shadow.core.props.shadow_node import ShadowNode
from src.client.ui.shadow.core.reconciler.record import ResourceRecord
from src.client.ui.shadow.tk.widgets.field import prop
from src.client.ui.values.geometry import Geometry


@dataclass(kw_only=True)
class SwTkWindow(ShadowNode):
    width: int = prop("geometry")
    height: int = prop("geometry")
    y: int = prop("geometry")
    x: int = prop("geometry")
    topmost: bool = prop("attributes", default=False)
    transparent_color: str | None = prop("attributes", default=None)
    override_redirect: bool = prop("special", default=False)

    @property
    def geometry(self) -> Geometry:
        return Geometry(self.x, self.y, self.width, self.height)

    @override
    def get_compatibility(self, prev) -> Literal["update", "replace", "recreate"]:
        prev = prev.node if isinstance(prev, ResourceRecord) else prev
        if prev is None:
            return "recreate"

        return "update"
