from dataclasses import dataclass, field
from tkinter import Label, Widget, Tk
from typing import Any, Callable, Literal, override

from src.client.ui.shadow.core.rendering.component import Component
from src.client.ui.shadow.tk.make_clickthrough import make_clickthrough
from src.client.ui.shadow.core.props.prop import prop
from src.client.ui.shadow.core.props.shadow_node import ShadowNode
from src.client.ui.shadow.core.reconciler.stateful_reconciler import StatefulReconciler
from src.client.ui.shadow.tk.widgets.widget import SwTkWidget


from src.client.ui.shadow.tk.window.reconcile_actions import TkWrapper
from src.client.ui.shadow.tk.window.window import SwTkWindow
from src.client.ui.values.font import Font


class TK[State]:
    _reconciler: StatefulReconciler[SwTkWindow]

    def __init__(self, render: Callable[[State], Component[SwTkWindow]]):
        self._reconciler = StatefulReconciler(TkWrapper, lambda x: TkWrapper.create(x))
        self.render = render

    def __call__(self, state: State):
        root = self.render(state)
        self._reconciler.reconcile(root)

    @dataclass()
    class Label(SwTkWidget):

        @property
        @override
        def tk_type(self) -> str:
            return "Label"

        text: str = prop("configure", default="")
        font: Font = prop(
            "configure",
            default=Font("Courier New", 18, "normal"),
            converter=lambda x: x.to_tk(),
        )
        ipadx: int = prop("pack", default=0)
        ipady: int = prop("pack", default=0)
        fill: Literal["both", "x", "y", "none"] = prop("pack", default="none")
        background: str = prop("configure", default="#000001")
        foreground: str = prop("configure", default="#ffffff")
        justify: str = prop("configure", default="center")
        relief: str = prop("configure", default="solid")
        borderwidth: int = prop("configure", default=0)

    Window = SwTkWindow
