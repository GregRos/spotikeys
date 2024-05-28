from dataclasses import dataclass
from typing import override

from client.desktop.desktop_status import DesktopExec
from src.ui import Component, Widget, Font, Label

header_c = "#20328F"


@dataclass
class DesktopCommandHeader(Component[Widget]):
    input: DesktopExec

    @override
    def render(self, yld, _):
        yld(
            Label(
                text=self.input.command.command.__str__().ljust(30),
                background=header_c,
                justify="left",
                foreground="#dddddd",
                font=Font(
                    family="Segoe UI Emoji",
                    size=13,
                    style="bold",
                ),
            ).Pack(
                anchor="w",
                ipadx=20,
                ipady=5,
                fill="both",
            )
        )
