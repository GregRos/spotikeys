import ctypes
from math import trunc
from tkinter import Tk, Label, SOLID, LEFT, CENTER
from typing import Tuple

from networkx import project


from src.client.kb.triggered_command import (
    ExecutedCommand,
    OkayCommand,
    TriggeredCommand,
)
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


def get_volume_line(info: VolumeInfo, _):
    empty = "◇"
    full = "◇" if info.mute else "◆"
    if info.mute:
        return f"🔇 {empty * 16}"
    full_boxes = trunc(info.volume / 100 * 16)
    return f"🔊 {full * full_boxes}{empty * (16 - full_boxes)}"


def get_progress_line(status: MediaStatus, _):
    remaining_time = format_duration(status.duration - status.position)
    full_blocks = round(float(status.progress / 100) * 9)
    progress_line = f"{ '▶' if status.is_playing else '⏸' } {'█' * full_blocks}{'░' * (9 - full_blocks)} {remaining_time}"
    return progress_line


MediaOkay = OkayCommand[MediaStatus]


def set_success(
    executed: OkayCommand[MediaStatus], target: TooltipRow[OkayCommand[MediaStatus]]
):
    if executed.triggered.command.code == "get_status":
        target.background("grey")
        return (
            f"💡 {str(executed.triggered).ljust(30)} {executed.duration * 1000:.0f}ms"
        )

    target.background("darkblue")
    return f"✅ {executed.triggered} {executed.duration * 1000:.0f}ms"


class MediaTooltip:
    _tk: Tk
    _pos: Tuple[int, int]
    _status: MediaStatus
    _error = False

    def __init__(self, tk: Tk):
        self._tk = tk
        self._pos = (-450, -350)
        tk.attributes("-topmost", 1, "-transparentcolor", "black")
        tk.wm_attributes("-topmost", True)
        tk.config(bg="black")
        tk.overrideredirect(True)
        self._command_line = TooltipRow[OkayCommand[MediaStatus]](
            tk,
            fill="both",
            bg="#000000",
            fg="#dddddd",
            ipadx=20,
            ipady=5,
            projection=set_success,
        )
        self._song_title_line = TooltipRow[MediaStatus](
            tk,
            projection=lambda x, _: x.title,
            fill="both",
            ipadx=15,
            bg="#000000",
            fg="#ffffff",
            font=("Segoe UI Emoji", 18),
        )
        self._song_artist_line = TooltipRow[MediaStatus](
            tk,
            projection=lambda x, _: x.artist,
            fill="x",
            bg="#000000",
            fg="#aaaafb",
            font=("Segoe UI Emoji", 14),
            ipadx=15,
        )
        self._progress_line = TooltipRow[MediaStatus](
            tk,
            projection=get_progress_line,
            fill="both",
            bg="#000000",
            fg="#ffffff",
            font=("Segoe UI Emoji", 12),
            ipadx=20,
            ipady=15,
        )

        self._song_volume_line = TooltipRow[VolumeInfo](
            tk,
            projection=get_volume_line,
            fill="both",
            bg="#000000",
            ipadx=40,
            ipady=15,
            fg="#00ff00",
            font=("Segoe UI Emoji", 12),
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

    def show(self):
        self._place_window()

    def _place_window(self):
        self._tk.wm_geometry("420x250+%d+%d" % self._normalize_pos(self._pos))
        self._tk.deiconify()
        self._tk.update_idletasks()

    def notify_command_start(self, command: TriggeredCommand):
        if self._error:
            self._error = False
            self._command_line.unplace()
            self._song_title_line.text(" ")
        self._command_line.text(f"⌛ {str(command).ljust(30)} ⌛⌛").background(
            "darkblue"
        ).font_size(12)
        self._place_window()
        self._tk.attributes("-alpha", 0.85)
        self._tk.update_idletasks()

    def notify_start_show_status(self):
        self._tk.attributes("-alpha", 1)
        self._command_line
        self._tk.attributes("-alpha", 0.85)
        self._tk.update_idletasks()

    def notify_show_status(self, exec: MediaOkay | None = None):
        self._tk.attributes("-alpha", 1)

        if exec:
            self._status = exec
            self._show_media(exec)
        self._place_window()
        self._tk.update_idletasks()

    def notify_command_done(self, finished: MediaOkay):
        self._tk.attributes("-alpha", 1)
        self._status = finished.result
        self._show_media(finished.result)
        self._place_window()
        self._tk.update_idletasks()

    def _show_media(self, exec: MediaOkay):
        status = exec.result
        self._command_line.value(exec).place()
        self._song_title_line.value(status).place()

        self._song_artist_line.value(status).place()

        self._progress_line.value(status).place()

        self._song_volume_line.value(status.volume).place()

        self._place_window()

    def hide(self):
        self._tk.withdraw()
        self._tk.update_idletasks()
