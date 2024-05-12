from dataclasses import dataclass, field
from tkinter import Label, Widget, Tk
from typing import Callable, override

from src.client.ui.shadow.core.rendering.component import Component
from src.client.ui.shadow.tk.make_clickthrough import make_clickthrough
from src.client.ui.shadow.core.props.prop import prop
from src.client.ui.shadow.core.reconciler.stateful_reconciler import StatefulReconciler


from src.client.ui.shadow.tk.window.reconcile_actions import TkWrapper
from src.client.ui.shadow.tk.window.window import SwTkWindow


class TK[State]:
    _reconciler: StatefulReconciler[SwTkWindow]

    def __init__(self, render: Callable[[State], Component[SwTkWindow]]):
        self._reconciler = StatefulReconciler(TkWrapper, lambda x: TkWrapper.create(x))
        self.render = render

    def __call__(self, state: State):
        root = self.render(state)
        self._reconciler.reconcile(root)

    Window = SwTkWindow
