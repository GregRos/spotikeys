from dataclasses import dataclass
from time import sleep
from src.ui.rendering.context import Ctx
from src.ui.model.component import Component
from src.ui import LabelNode, WidgetNode
from src.ui import WindowComponentMount
from src.ui import Window
from src.log_config import setup_logging

setup_logging()


@dataclass(kw_only=True)
class StuffComponent(Component[WidgetNode]):
    text: str

    def render(self, _):
        yield LabelNode(
            text=self.text, background="#000001", foreground="#ffffff"
        ).pack(ipadx=20, ipady=15, fill="both")


@dataclass(kw_only=True)
class WindowComponent(Component[Window]):

    def render(self, ctx: Ctx):
        yield Window(
            topmost=True, background="black", transparent_color="black", alpha=85
        ).geometry(width=500, height=500, x=500, y=500)[
            StuffComponent(text=ctx.text), StuffComponent(text=ctx.text)
        ]


MyTK = WindowComponentMount(WindowComponent())

MyTK(text="Hello, World!")
sleep(2)
MyTK(text="Hello again!")
