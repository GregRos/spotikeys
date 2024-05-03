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
from src.client.ui.binding.active_value import ActiveValue
from src.client.ui.binding.bindable import bindable

from src.client.ui.command_header import CommandColors, CommandHeader
from src.client.ui.framework.component import Component
from src.client.ui.values.geometry import Geometry
from src.client.ui.framework.owner import UiRoot
from src.client.ui.framework.tooltip_row import TooltipRow
from src.client.ui.media_display import MediaDisplay
from src.client.volume import VolumeInfo
from src.commanding.commands import Command
from .framework.make_clickthrough import make_clickthrough
from src.now_playing import MediaStatus

ctypes.windll.shcore.SetProcessDpiAwareness(1)


MediaOkay = OkayCommand[MediaStatus]
MediaFailed = FailedCommand
MediaExecuted = MediaOkay | MediaFailed
MediaStageMessage = MediaExecuted | TriggeredCommand

justify = 24


@dataclass
class ActionHUD(Component):
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
