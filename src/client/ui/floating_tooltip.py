import ctypes
from logging import getLogger
from math import trunc
from tkinter import Tk, Label, SOLID, LEFT, CENTER
from typing import Tuple


from src.client.kb.triggered_command import (
    FailedCommand,
    OkayCommand,
    TriggeredCommand,
)
from src.client.ui.framework.active_value import ActiveValue
from src.client.ui.framework.bindable_property import bindable
from src.client.ui.framework.lbl import UiOwner
from src.client.ui.tooltip_row import TooltipRow
from src.client.volume import VolumeInfo
from src.commanding.commands import Command
from .make_clickthrough import make_clickthrough
from src.now_playing import MediaStatus

ctypes.windll.shcore.SetProcessDpiAwareness(1)


def format_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{int(minutes):02d}:{int(seconds):02d}"


def truncate_text(text: str, max_length: int) -> str:
    if len(text) > max_length:
        return text[: max_length - 1] + "⋯"
    return text


def get_volume_line(info: VolumeInfo):
    empty = "◇"
    full = "◇" if info.mute else "◆"
    if info.mute:
        return f"🔇 {empty * 16}"
    full_boxes = trunc(info.volume / 100 * 16)
    return f"🔊 {full * full_boxes}{empty * (16 - full_boxes)}"


def get_progress_line(status: MediaStatus):
    remaining_time = format_duration(status.duration - status.position)
    full_blocks = round(float(status.progress / 100) * 9)
    progress_line = f"{ '▶' if status.is_playing else '⏸' } {'█' * full_blocks}{'░' * (9 - full_blocks)} {remaining_time}"
    return progress_line


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


class MediaTooltip(UiOwner[MediaStageMessage]):
    _tk: Tk
    _pos: Tuple[int, int]
    _error = False

    def __init__(self):
        super().__init__()
        tk = self._tk
        self._pos = (-450, -350)
        via = self.value
        self.value.tap_after(self.on_after_value_change).subscribe()
        tk.attributes("-topmost", 1, "-transparentcolor", "black")
        tk.wm_attributes("-topmost", True)
        tk.config(bg="black")
        tk.overrideredirect(True)
        self._error = Label(background="")
        self._command_line = (
            self._ToolTipRow()
            .text(" ")
            .text(via.map(get_command_line))
            .background("black")
            .fill("both")
            .foreground("#dddddd")
            .ipadx(20)
            .ipady(5)
            .background(via.map(get_header_bg))
            .font(("Segoe UI Emoji", 12))
            .font_size(via.map(lambda x: 18 if isinstance(x, FailedCommand) else 12))
        )
        self._song_title_line = (
            self._ToolTipRow()
            .text(" ")
            .text(
                via.of_type(OkayCommand)
                .map(lambda x: x.result)
                .map(lambda x: truncate_text(x.title, 30))
            )
            .ipadx(15)
            .fill("both")
            .background("#000001")
            .foreground("#ffffff")
            .font(("Segoe UI Emoji", 18))
        )
        self._song_artist_line = (
            self._ToolTipRow()
            .text(" ")
            .text(
                via.of_type(OkayCommand).map(
                    lambda x: truncate_text(x.result.artist, 30)
                )
            )
            .fill("x")
            .ipadx(15)
            .background("#000001")
            .foreground("#aaaafb")
            .font(("Segoe UI Emoji", 14))
        )
        self._progress_line = (
            self._ToolTipRow()
            .text(" ")
            .text(
                via.of_type(OkayCommand).map(lambda x: x.result).map(get_progress_line)
            )
            .fill("both")
            .background("#000001")
            .foreground("#ffffff")
            .font(("Segoe UI Emoji", 15))
            .ipadx(20)
            .ipady(15)
        )

        self._song_volume_line = (
            self._ToolTipRow()
            .text(" ")
            .text(
                via.of_type(OkayCommand)
                .map(lambda x: x.result.volume)
                .map(get_volume_line)
            )
            .fill("both")
            .background("#000001")
            .foreground("#00ff00")
            .font(("Segoe UI Emoji", 13))
            .ipadx(40)
            .ipady(15)
        )
        self._tk.update_idletasks()

    def _normalize_pos(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        pos_x, pos_y = pos
        screen_width = self._tk.winfo_screenwidth()
        screen_height = self._tk.winfo_screenheight()
        if pos_x < 0:
            pos_x = screen_width + pos_x
        if pos_y < 0:
            pos_y = screen_height + pos_y
        return pos_x, pos_y

    def _place_window(self, *excluded: TooltipRow):
        self._tk.wm_geometry("420x250+%d+%d" % self._normalize_pos(self._pos))
        self._tk.deiconify()
        labels: list[TooltipRow] = [
            self._command_line,
            self._song_title_line,
            self._song_artist_line,
            self._progress_line,
            self._song_volume_line,
        ]

        for label in labels:
            if label in excluded:
                label.unplace()
            else:
                label.place()

    def on_after_value_change(self, value: MediaStageMessage):
        match value:
            case FailedCommand():
                self._error = True
                self._place_window(self._song_artist_line, self._progress_line)
                return
            case TriggeredCommand():
                self._tk.attributes("-alpha", 0.85)
                self._place_window()
                return
            case OkayCommand():
                if value.command.is_command("show_status"):
                    return
                self.auto_hide_after(3, value)
                self._tk.attributes("-alpha", 1)
                self._place_window()
                return

    def hide(self):
        self._tk.withdraw()
        self._tk.update_idletasks()
