from dataclasses import dataclass
from typing import override

from client.desktop.desktop_status import DesktopExec
from src.ui import Component, Widget, Font, Label


@dataclass
class DesktopCommandHeader(Component[Widget]):
    input: DesktopExec

    @override
    def render(self, yld, _):
        yld(
            Label(
                text=self.input.command.__str__(),
                background="black",
                foreground="white",
                font=Font(
                    family="Segoe UI Emoji",
                    size=13,
                    style="bold",
                ),
            ).Pack(
                ipadx=20,
                ipady=5,
                fill="both",
            )
        )
