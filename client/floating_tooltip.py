from asyncio import sleep
import ctypes
from dataclasses import dataclass
from typing import override


from client.error import FailDisplay
from client.media_types import MediaStageMessage
from src.kb.triggered_command import (
    FailedCommand,
    OkayCommand,
    TriggeredCommand,
)


from client.command_header import CommandHeader
from src.ui import Window, Ctx, Component, Widget
from client.media_display import MediaDisplay
from src.spotify.now_playing import MediaStatus

ctypes.windll.shcore.SetProcessDpiAwareness(1)


justify = 24


@dataclass
class ActionHUD(Component[Window]):

    def render(self, yld, ctx):
        if ctx.hidden == True:
            return
        yld(
            Window(
                background="#000001",
                topmost=True,
                transparent_color="black",
                override_redirect=True,
                alpha=85 if isinstance(ctx.executed, TriggeredCommand) else 100,
            )
            .Geometry(
                width=420,
                height=250,
                x=-450,
                y=-350,
            )
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
                CommandHeader(
                    input=self.executed,
                    justify=justify,
                    colors={
                        "status": "grey",
                        "trigger": "blue",
                        "okay": "green",
                        "failed": "red",
                    },
                )
            )
            if isinstance(self.executed, FailedCommand):
                yld(FailDisplay(executed=self.executed))
            else:
                yld(MediaDisplay(status=self.previous))
