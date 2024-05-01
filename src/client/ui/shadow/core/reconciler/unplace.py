from src.client.ui.shadow.core.base import ShadowNode


from tkinter import Widget


class Unplace:
    def __init__(self, prev: ShadowNode):
        self.prev = prev

    @property
    def key(self) -> str:
        return self.prev.key

    @property
    def tk_type(self) -> str:
        return self.prev.tk_type

    def __call__(self, target: Widget):
        target.pack_forget()
