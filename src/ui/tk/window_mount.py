from typing import Any
from src.ui.model.context import Ctx
from src.ui.rendering.renderer import ComponentMount
from src.ui.rendering.stateful_reconciler import StatefulReconciler
from src.ui.model.component import Component
from src.ui.tk.window_wrapper import WindowWrapper
from src.ui.tk.window import Window


class WindowMount(ComponentMount):
    def __init__(self, root: Component):
        self._ctx = Ctx()
        reconciler = StatefulReconciler[Window](
            WindowWrapper, lambda x: WindowWrapper.create(x, self._ctx)
        )
        super().__init__(reconciler, self._ctx, root)
