from dataclasses import dataclass
from time import sleep
from src.ui.model.context import Ctx
from src.ui.model.component import Component
from src.ui import Label, Widget, Window, WindowMount
from src.setup_logging import setup_logging

setup_logging()


@dataclass(kw_only=True)
class StuffComponent(Component[Widget]):
    text: str

    def render(self, yld, _):
        yld(
            Label(text=self.text, background="#000001", foreground="#ffffff").Pack(
                ipadx=20, ipady=15, fill="both"
            )
        )


@dataclass(kw_only=True)
class WindowComponent(Component[Window]):

    def render(self, yld, ctx: Ctx):
        yld(
            Window(
                topmost=True, background="black", transparent_color="black", alpha=85
            )
            .Geometry(width=500, height=500, x=500, y=500, anchor_point="lt")
            .child(StuffComponent(text=ctx.text))
        )


MyTK = WindowMount(WindowComponent())

MyTK(text="Hello, World!")
sleep(2)
MyTK(text="Hello again!")
