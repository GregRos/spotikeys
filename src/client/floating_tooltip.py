from asyncio import sleep
import ctypes
from dataclasses import dataclass
from typing import override


from src.client.media_types import MediaStageMessage
from src.kb.triggered_command import (
    FailedCommand,
    OkayCommand,
    TriggeredCommand,
)


from src.client.command_header import CommandHeader
from src.ui import Window, Ctx, Component, Widget
from src.client.media_display import MediaDisplay
from src.now_playing import MediaStatus

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
            ).Geometry(
                width=420,
                height=250,
                x=-450,
                y=-350,
            )[
                self.Inner(executed=ctx.executed, previous=ctx.last_status)
            ]
        )

    @dataclass
    class Inner(Component[Widget]):
        executed: MediaStageMessage
        previous: MediaStatus

        @override
        def render(self, yld, ctx: Ctx):
            if isinstance(self.executed, FailedCommand):
                raise ValueError("Failed command should not be rendered")
            if ctx.hidden:
                return
            yld(
                CommandHeader(
                    input=self.executed,
                    justify=justify,
                    colors={
                        "status": "red",
                        "trigger": "grey",
                        "okay": "green",
                    },
                )
            )
            yld(MediaDisplay(status=self.previous))
