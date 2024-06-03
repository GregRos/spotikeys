from asyncio import sleep
import ctypes
from dataclasses import dataclass
import itertools
from typing import Any, Literal, override


from client.desktop.command_header import DesktopCommandHeader
from client.desktop.desktop_status import App, DesktopExec
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

        def _win_title(self, cmd: OkayCommand, apps: tuple[App, ...]):
            titles = list(map(lambda x: f"{cmd.command.emoji} {x.title}", apps))
            elipsis = None
            if len(titles) > 3:
                titles = titles[:3]
                elipsis = f"⋯ ({len(apps) - 3}) more ⋯"
            titles = map(lambda x: truncate_text(x, 34), titles)
            titles = "\n".join(titles)
            yield Label(
                text=f"{titles}",
                background=green_c,
                justify="left",
                foreground="#ffffff",
                font=Font(family="Segoe UI Emoji", size=10, style="bold"),
            ).Pack(ipadx=0, anchor="w", fill="both")
            if elipsis:
                yield Label(
                    text=elipsis,
                    background=green_c,
                    justify="center",
                    foreground="#ffffff",
                    font=Font(family="Segoe UI Emoji", size=8),
                ).Pack(ipadx=0, fill="x")

        @override
        def render(self, yld, _):
            result = self.executed.result
            yld(DesktopCommandHeader(input=result))
            orig_desktop = (
                result.shove.start if result.shove else result.pan.start  # type: ignore
            )
            new_desktop = result.shove.end if result.shove else result.pan.end  # type: ignore
            yld(
                Label(
                    text=f"🖥️ {new_desktop.name}{" 👁️" if result.pan else ""}",
                    background=green_c,
                    foreground="#ffffff",
                    font=Font(
                        family="Segoe UI Emoji",
                        size=17,
                        style="normal",
                    ),
                ).Pack(ipadx=15, fill="both")
            )
            if result.shove:
                yld(self._win_title(self.executed, result.shove.apps))

            yld(
                Label(
                    text=f"↩️ {orig_desktop.name}",
                    background=old_desktop_c,
                    foreground="#ffffff",
                    justify="center",
                    font=Font(
                        family="Segoe UI Emoji",
                        size=11,
                        style="normal",
                    ),
                ).Pack(ipadx=15, fill="x")
            )
