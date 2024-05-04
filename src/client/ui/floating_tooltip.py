import ctypes
from dataclasses import dataclass
from logging import getLogger
from math import trunc
from threading import Thread
from time import sleep
from tkinter import Tk, Label, SOLID, LEFT, CENTER, Widget
from typing import Generator, Tuple, override

from attr import field


from src.client.kb.triggered_command import (
    FailedCommand,
    OkayCommand,
    TriggeredCommand,
)


from src.client.ui.command_header import CommandColors, CommandHeader
from src.client.ui.shadow.core.component import Component
from src.client.ui.shadow.tk.nodes import TK
from src.client.ui.shadow.tk.widgets.widget import WidgetComponent
from src.client.ui.shadow.tk.window.window import WindowComponent
from src.client.ui.values.geometry import Geometry
from src.client.ui.framework.tooltip_row import TooltipRow
from src.client.ui.media_display import MediaDisplay
from src.client.volume import VolumeInfo
from src.commanding.commands import Command
from .shadow.tk.make_clickthrough import make_clickthrough
from src.now_playing import MediaStatus

ctypes.windll.shcore.SetProcessDpiAwareness(1)


MediaOkay = OkayCommand[MediaStatus]
MediaFailed = FailedCommand
MediaExecuted = MediaOkay | MediaFailed
MediaStageMessage = MediaExecuted | TriggeredCommand

justify = 24


@dataclass
class ActionHUD(WindowComponent):
    executed: MediaStageMessage
    previous: MediaStatus = field(default=None, init=False)

    def render(self):
        yield TK.Window(
            width=420,
            height=250,
            x=-450,
            y=-350,
            topmost=True,
        )[self.Inner(executed=self.executed)]

    @dataclass
    class Inner(WidgetComponent):
        executed: MediaStageMessage
        previous: MediaStatus = field(default=None, init=False)

        @override
        def render(self):
            if isinstance(self.executed, FailedCommand):
                raise ValueError("Failed command should not be rendered")
            if isinstance(self.executed, OkayCommand):
                self.previous = self.executed.result
            yield CommandHeader(
                input=self.executed,
                justify=justify,
                colors=CommandColors(
                    status="red",
                    trigger="grey",
                    okay="green",
                ),
            )
            yield MediaDisplay(status=self.previous)
