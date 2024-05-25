from tkinter import Tk
from src.ui.core.context import Ctx
from src.ui.core.renderer import ComponentMount
from src.ui.core.stateful_reconciler import StatefulReconciler
from src.ui.model.component import Component
from src.ui.tk.widgets.widget import WidgetNode
from src.ui.tk.widgets.widget_wrapper import WidgetWrapper


class WidgetComponentMount(ComponentMount):
    def __init__(self, tk: Tk, context: Ctx, root: Component):
        reconciler = StatefulReconciler[WidgetNode](
            WidgetWrapper, lambda x: WidgetWrapper.create(tk, x)
        )
        super().__init__(reconciler, context, root)
