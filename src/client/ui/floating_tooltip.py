from asyncio import sleep
import ctypes
from dataclasses import dataclass
from typing import override


from src.client.kb.triggered_command import (
    FailedCommand,
    OkayCommand,
    TriggeredCommand,
)


from src.client.ui.command_header import CommandHeader
from src.client.ui.shadow.core.context import Ctx
from src.client.ui.shadow.tk.widgets.widget import WidgetComponent
from src.client.ui.shadow.tk.window.window import SwTkWindow, WindowComponent
from src.client.ui.media_display import MediaDisplay
from src.now_playing import MediaStatus

ctypes.windll.shcore.SetProcessDpiAwareness(1)


MediaOkay = OkayCommand[MediaStatus]
MediaFailed = FailedCommand
MediaExecuted = MediaOkay | MediaFailed
MediaStageMessage = MediaExecuted | TriggeredCommand

justify = 24


@dataclass
class ActionHUD(WindowComponent):

    def render(self, ctx):
        if ctx.hidden == True:
            return
        yield SwTkWindow(
            background="#000001",
            topmost=True,
            transparent_color="black",
            override_redirect=True,
            alpha=85 if isinstance(ctx.executed, TriggeredCommand) else 100,
        ).geometry(
            width=420,
            height=250,
            x=-450,
            y=-350,
        )[
            self.Inner(executed=ctx.executed, previous=ctx.last_status)
        ]

    @dataclass
    class Inner(WidgetComponent):
        executed: MediaStageMessage
        previous: MediaStatus

        @override
        def render(self, ctx: Ctx):
            if isinstance(self.executed, FailedCommand):
                raise ValueError("Failed command should not be rendered")
            if ctx.hidden:
                return
            yield CommandHeader(
                input=self.executed,
                justify=justify,
                colors={
                    "status": "red",
                    "trigger": "grey",
                    "okay": "green",
                },
            )
            yield MediaDisplay(status=self.previous)
