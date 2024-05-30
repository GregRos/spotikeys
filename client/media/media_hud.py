from asyncio import sleep
import ctypes
from dataclasses import dataclass
from typing import override


from client.desktop.desktop_status import DesktopExec
from client.error import FailDisplay
from client.media.media_types import MediaStageMessage
from src.kb.triggered_command import (
    FailedCommand,
    OkayCommand,
    TriggeredCommand,
)


from client.media.command_header import MediaCommandHeader
from src.ui import Window, Ctx, Component, Widget
from client.media.media_display import MediaDisplay
from src.spotify.now_playing import MediaStatus

ctypes.windll.shcore.SetProcessDpiAwareness(1)


justify = 24


@dataclass
class MediaHUD(Component[Window]):

    def render(self, yld, ctx):
        if ctx.hidden == True:
            return
        yld(
            Window(
                background="#000000",
                topmost=True,
                transparent_color="black",
                override_redirect=True,
                alpha=85 if isinstance(ctx.executed, TriggeredCommand) else 100,
            )
            .Geometry(width=420, height=250, x=-5, y=-85, anchor_point="rb")
            .child(self.Inner(executed=ctx.executed, previous=ctx.last_status))
        )

    @dataclass
    class Inner(Component[Widget]):
        executed: MediaStageMessage
        previous: MediaStatus

        @override
        def render(self, yld, ctx: Ctx):

            if ctx.hidden:
                return
            yld(
                MediaCommandHeader(
                    input=self.executed,
                    justify=justify,
                    colors={
                        "status": "#484D49",
                        "trigger": "#161670",
                        "okay": "#2E620C",
                        "failed": "#980E0E",
                    },
                )
            )
            if isinstance(self.executed, FailedCommand):
                yld(FailDisplay(executed=self.executed))
            else:
                yld(MediaDisplay(status=self.previous))
