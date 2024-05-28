from asyncio import sleep
import ctypes
from dataclasses import dataclass
from typing import override


from client.desktop.command_header import DesktopCommandHeader
from client.desktop.desktop_status import DesktopExec
from client.error import FailDisplay
from client.media.media_display import MediaDisplay
from client.media.media_types import MediaStageMessage
from src.kb.triggered_command import (
    FailedCommand,
    OkayCommand,
    TriggeredCommand,
)


from src.ui import Window, Ctx, Component, Widget


justify = 24


@dataclass
class DestkopHUD(Component[Window]):

    def render(self, yld, ctx):
        if ctx.hidden == True:
            return
        yld(
            Window(
                background="#000001",
                topmost=True,
                transparent_color="black",
                override_redirect=True,
            )
            .Geometry(width=500, height=300, x=-5, y=-85, anchor_point="rb")
            .child(self.Inner(executed=ctx.executed))
        )

    @dataclass
    class Inner(Component[Widget]):
        executed: DesktopExec

        @override
        def render(self, yld, ctx: Ctx):

            if ctx.hidden:
                return
            yld(DesktopCommandHeader(input=self.executed))
