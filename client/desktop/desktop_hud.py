from asyncio import sleep
import ctypes
from dataclasses import dataclass
from typing import Any, Literal, override

from click import BOOL


from client.desktop.command_header import DesktopCommandHeader
from client.desktop.desktop_status import DesktopExec
from client.error import FailDisplay
from client.media.media_display import MediaDisplay, truncate_text
from client.media.media_types import MediaStageMessage
from src.kb.triggered_command import (
    FailedCommand,
    OkayCommand,
    TriggeredCommand,
)


from src.ui import Window, Ctx, Component, Widget
from src.ui import Font, Label


justify = 24

green_c = "#101947"
old_desktop_c = "#3A467E"


@dataclass
class DestkopHUD(Component[Window]):

    def render(self, yld, ctx):
        if ctx.hidden == True:
            return
        yld(
            Window(
                background="#000000",
                topmost=True,
                transparent_color="black",
                override_redirect=True,
            )
            .Geometry(width=420, height=250, x=-5, y=-85, anchor_point="rb")
            .child(self.Inner(executed=ctx.executed))
        )

    @dataclass
    class Inner(Component[Widget]):
        executed: OkayCommand[DesktopExec]

        def _win_title(self, title: str):
            return Label(
                text=f"{truncate_text(title, 50)}",
                wraplength=300,
                background=green_c,
                foreground="#ffffff",
                font=Font(family="Segoe UI Emoji", size=12),
            ).Pack(ipadx=5, fill="both")

        @override
        def render(self, yld, _):
            executed = self.executed.result
            yld(DesktopCommandHeader(input=executed))
            orig_desktop = (
                executed.shove.start if executed.shove else executed.pan.start  # type: ignore
            )
            new_desktop = executed.shove.end if executed.shove else executed.pan.end  # type: ignore
            yld(
                Label(
                    text=f"🖥️ {new_desktop.name}{" 👁️" if executed.pan else ""}",
                    background=green_c,
                    foreground="#ffffff",
                    font=Font(
                        family="Segoe UI Emoji",
                        size=17,
                        style="normal",
                    ),
                ).Pack(ipadx=15, fill="both")
            )
            if executed.shove:
                yld(self._win_title(executed.shove.app.title))

            yld(
                Label(
                    text=f"🖥️ {orig_desktop.name}",
                    background=old_desktop_c,
                    foreground="#ffffff",
                    font=Font(
                        family="Segoe UI Emoji",
                        size=11,
                        style="normal",
                    ),
                ).Pack(ipadx=15, fill="both")
            )
