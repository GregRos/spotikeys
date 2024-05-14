from tkinter import Tk
from src.client.ui.shadow.core.context import Ctx
from src.client.ui.shadow.core.renderer import ComponentMount
from src.client.ui.shadow.core.stateful_reconciler import StatefulReconciler
from src.client.ui.shadow.tk.widgets.widget import WidgetNode
from src.client.ui.shadow.tk.widgets.widget_wrapper import WidgetWrapper


class WidgetComponentMount(ComponentMount):
    def __init__(self, tk: Tk, context: Ctx):
        reconciler = StatefulReconciler[WidgetNode](
            WidgetWrapper, lambda x: WidgetWrapper.create(tk, x)
        )
        super().__init__(reconciler, context)
