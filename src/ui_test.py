from dataclasses import dataclass
from time import sleep
from src.client.ui.framework.component import Component
from src.client.ui.shadow.tk.nodes import TK
from src.client.ui.shadow.tk.widgets.widget import SwTkWidget
from src.client.ui.shadow.tk.window.window import SwTkWindow
from src.log_config import setup_logging

setup_logging()


@dataclass
class StuffComponent(Component[SwTkWidget]):
    text: str

    def render(self):
        yield TK.Label(text=self.text, background="#000001", foreground="#ffffff")


@dataclass
class WindowComponent(Component[SwTkWindow]):
    text: str

    def render(self):
        yield TK.Window(
            width=800,
            height=600,
            x=100,
            y=100,
            topmost=True,
        )[StuffComponent(text=self.text)]


MyTK = TK()

MyTK.mount(WindowComponent("Hello, World!"))
sleep(10)
MyTK.mount(WindowComponent("Boo!"))
