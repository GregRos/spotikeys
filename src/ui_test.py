from dataclasses import dataclass
from time import sleep
from src.client.ui.shadow.core.component import Component
from src.client.ui.shadow.tk.nodes import TK
from src.client.ui.shadow.tk.widgets.widget import SwTkWidget
from src.client.ui.shadow.tk.window.window import SwTkWindow
from src.log_config import setup_logging

setup_logging()


@dataclass(kw_only=True)
class StuffComponent(Component[SwTkWidget]):
    text: str

    def render(self):
        yield TK.Label(text=self.text, background="#000001", foreground="#ffffff")


@dataclass(kw_only=True)
class WindowComponent(Component[SwTkWindow]):
    text: str

    def render(self):
        yield TK.Window(
            width=1200,
            height=1200,
            x=100,
            y=100,
            topmost=True,
        )[StuffComponent(text=self.text), StuffComponent(text=self.text)]


MyTK = TK[str](lambda s: WindowComponent(text=s))

MyTK("Hello, World!")
sleep(2)
MyTK("Hello again!")
