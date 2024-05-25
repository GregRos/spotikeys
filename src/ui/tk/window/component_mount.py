from typing import Any
from src.ui.rendering.context import Ctx
from src.ui.rendering.renderer import ComponentMount
from src.ui.rendering.stateful_reconciler import StatefulReconciler
from src.ui.model.component import Component
from src.ui.tk.window.wrapper import TkWrapper
from src.ui.tk.window.window import Window


class WindowComponentMount(ComponentMount):
    def __init__(self, root: Component):
        self._ctx = Ctx()
        reconciler = StatefulReconciler[Window](
            TkWrapper, lambda x: TkWrapper.create(x, self._ctx)
        )
        super().__init__(reconciler, self._ctx, root)
