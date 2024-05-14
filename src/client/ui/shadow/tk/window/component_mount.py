from src.client.ui.shadow.core.context import Ctx
from src.client.ui.shadow.core.renderer import ComponentMount
from src.client.ui.shadow.core.stateful_reconciler import StatefulReconciler
from src.client.ui.shadow.tk.window.wrapper import TkWrapper
from src.client.ui.shadow.tk.window.window import SwTkWindow


class WindowComponentMount(ComponentMount):
    def __init__(self, context: Ctx):
        reconciler = StatefulReconciler[SwTkWindow](
            TkWrapper, lambda x: TkWrapper.create(x, context)
        )
        super().__init__(reconciler, context)
