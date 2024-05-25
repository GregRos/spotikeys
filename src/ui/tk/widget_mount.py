from tkinter import Tk
from src.ui.model.context import Ctx
from src.ui.rendering.renderer import ComponentMount
from src.ui.rendering.stateful_reconciler import StatefulReconciler
from src.ui.model.component import Component
from src.ui.tk.widget import Widget
from src.ui.tk.widget_wrapper import WidgetWrapper


class WidgetMount(ComponentMount):
    def __init__(self, tk: Tk, context: Ctx, root: Component):
        reconciler = StatefulReconciler[Widget](
            WidgetWrapper, lambda x: WidgetWrapper.create(tk, x)
        )
        super().__init__(reconciler, context, root)
