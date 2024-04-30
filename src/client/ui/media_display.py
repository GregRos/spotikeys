from math import trunc
from tkinter import Tk
from src.client.kb.triggered_command import OkayCommand
from src.client.ui.binding.active_value import ActiveValue
from src.client.ui.framework.component import (
    Component,
)
from src.client.volume import VolumeInfo
from src.now_playing import MediaStatus


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


class MediaDisplay(Component):

    def __init__(self, parent: Component):
        super().__init__(parent)
        self.value = self.ActiveValue[MediaStatus](
            "value", scheduler=lambda f: self.tk.after(0, f)
        )
        via = self.value
        self._song_title_line = (
            self._ToolTipRow()
            .text(" ")
            .text(via.map(lambda x: truncate_text(x.title, 30)))
            .ipadx(15)
            .fill("both")
            .background("#000001")
            .foreground("#ffffff")
            .font_family("Segoe UI Emoji")
            .font_size(18)
        )
        self._song_artist_line = (
            self._ToolTipRow()
            .text(" ")
            .text(via.map(lambda x: truncate_text(x.artist, 30)))
            .fill("both")
            .ipadx(15)
            .background("#000001")
            .foreground("#aaaafb")
            .font_family("Segoe UI Emoji")
            .font_size(15)
        )
        self._progress_line = (
            self._ToolTipRow()
            .text(" ")
            .text(via.map(get_progress_line))
            .fill("both")
            .background("#000001")
            .foreground("#ffffff")
            .font_family("Segoe UI Emoji")
            .font_size(14)
            .ipadx(20)
            .ipady(15)
        )

        self._song_volume_line = (
            self._ToolTipRow()
            .text(" ")
            .text(via.map(lambda x: x.volume).map(get_volume_line))
            .fill("both")
            .background("#000001")
            .foreground("#00ff00")
            .font_family("Segoe UI Emoji")
            .font_size(13)
            .ipadx(40)
            .ipady(13)
        )

    def render(self):
        yield from [
            self._song_title_line,
            self._song_artist_line,
            self._progress_line,
            self._song_volume_line,
        ]
