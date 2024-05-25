from dataclasses import dataclass
from time import sleep
from src.ui.model.context import Ctx
from src.ui.model.component import Component
from src.ui import Label, Widget, Window, WindowMount
from src.log_config import setup_logging

setup_logging()


@dataclass(kw_only=True)
class StuffComponent(Component[Widget]):
    text: str

    def render(self, _):
        yield Label(text=self.text, background="#000001", foreground="#ffffff").pack(
            ipadx=20, ipady=15, fill="both"
        )


@dataclass(kw_only=True)
class WindowComponent(Component[Window]):

    def render(self, ctx: Ctx):
        yield Window(
            topmost=True, background="black", transparent_color="black", alpha=85
        ).geometry(width=500, height=500, x=500, y=500)[
            StuffComponent(text=ctx.text), StuffComponent(text=ctx.text)
        ]


MyTK = WindowMount(WindowComponent())

MyTK(text="Hello, World!")
sleep(2)
MyTK(text="Hello again!")
