from dataclasses import dataclass
from time import sleep
from src.client.ui.shadow.core.context import Ctx
from src.client.ui.shadow.model.components.component import Component
from src.client.ui.shadow.tk.widgets.widget import LabelNode, WidgetNode
from src.client.ui.shadow.tk.window.component_mount import WindowComponentMount
from src.client.ui.shadow.tk.window.window import SwTkWindow
from src.log_config import setup_logging

setup_logging()


@dataclass(kw_only=True)
class StuffComponent(Component[WidgetNode]):
    text: str

    def render(self, _):
        yield LabelNode(text=self.text, background="#000001", foreground="#ffffff")


@dataclass(kw_only=True)
class WindowComponent(Component[SwTkWindow]):

    def render(self, ctx: Ctx):
        yield SwTkWindow(
            topmost=True, background="black", transparent_color="black", alpha=85
        )[StuffComponent(text=ctx.text), StuffComponent(text=ctx.text)]


MyTK = WindowComponentMount(WindowComponent())

MyTK(text="Hello, World!")
sleep(2)
MyTK(text="Hello again!")
