import ctypes
from logging import getLogger
from math import trunc
from threading import Thread
from time import sleep
from tkinter import Tk, Label, SOLID, LEFT, CENTER, Widget
from typing import Generator, Tuple


from src.client.kb.triggered_command import (
    FailedCommand,
    OkayCommand,
    TriggeredCommand,
)
from src.client.ui.binding.active_value import ActiveValue
from src.client.ui.binding.bindable import bindable

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


def get_command_line(executed: MediaStageMessage):
    if isinstance(executed, FailedCommand):
        return (
            f"❌ {str(executed.triggered).ljust(28)} {executed.duration * 1000:.0f}ms"
        )

    if isinstance(executed, TriggeredCommand):
        return (
            f"⌛ {str(executed).ljust(justify)} ⌛⌛"
            if executed.code != "show_status"
            else f"💡 {str(executed).ljust(justify)} ⌛⌛"
        )

    if (
        isinstance(executed, OkayCommand)
        and executed.triggered.command.code == "show_status"
    ):
        return f"💡 {str(executed.triggered).ljust(justify)} ⌛⌛"

    return f"✅ {executed.triggered.__str__().ljust(justify)} {executed.duration * 1000:.0f}ms"


def get_header_bg(executed: MediaStageMessage):
    if isinstance(executed, FailedCommand):
        return "red"
    if isinstance(executed, TriggeredCommand):
        return "grey" if executed.code == "show_status" else "darkblue"
    if (
        isinstance(executed, OkayCommand)
        and executed.triggered.command.code == "show_status"
    ):
        return "grey"
    return "green"


class ActionHUD(Component):
    _media_display: MediaDisplay

    def __init__(self, parent: Component | Tk):
        super().__init__(parent)
        via = self.value = self.ActiveValue[MediaStageMessage]("value")
        self._command_line = (
            self._ToolTipRow()
            .text(" ")
            .text(via.map(get_command_line))
            .background("#000001")
            .fill("both")
            .foreground("#dddddd")
            .ipadx(20)
            .ipady(5)
            .background(via.map(get_header_bg))
            .font_family("Segoe UI Emoji")
            .font_size(via.map(lambda x: 18 if isinstance(x, FailedCommand) else 12))
        )
        self._media_display = MediaDisplay(self)
        self._media_display.value.bind(via.of_type(OkayCommand).map(lambda x: x.result))

    def render(self) -> Generator[Widget | Component, None, None]:
        yield self._command_line
        yield self._media_display

    def hide(self):
        self.tk.withdraw()
        self.tk.update_idletasks()
