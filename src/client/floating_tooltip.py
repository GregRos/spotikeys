from asyncio import sleep
import ctypes
from pydantic.dataclasses import dataclass
from typing import override


from src.kb.triggered_command import (
    FailedCommand,
    OkayCommand,
    TriggeredCommand,
)


from src.client.command_header import CommandHeader
from src.ui.rendering.context import Ctx
from src.ui.tk.widgets.widget import WidgetComponent
from src.ui.tk.window.window import Window, WindowComponent
from src.client.media_display import MediaDisplay
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
        yield Window(
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
