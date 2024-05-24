from typing import Any
from src.client.ui.shadow.core.context import Ctx
from src.client.ui.shadow.core.renderer import ComponentMount
from src.client.ui.shadow.core.stateful_reconciler import StatefulReconciler
from src.client.ui.shadow.model.components.component import Component
from src.client.ui.shadow.tk.window.wrapper import TkWrapper
from src.client.ui.shadow.tk.window.window import SwTkWindow


class WindowComponentMount(ComponentMount):
    def __init__(self, root: Component):
        self._ctx = Ctx()
        reconciler = StatefulReconciler[SwTkWindow](
            TkWrapper, lambda x: TkWrapper.create(x, self._ctx)
        )
        super().__init__(reconciler, self._ctx, root)

    def __call__(self, **ctx_args: Any):
        self._ctx(**ctx_args)

    @property
    def ctx(self):
        return self._ctx
