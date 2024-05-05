from dataclasses import dataclass
from math import trunc
from tkinter import Tk
from src.client.kb.triggered_command import OkayCommand
from src.client.ui.binding.active_value import ActiveValue
from src.client.ui.shadow.core.rendering.component import (
    Component,
)
from src.client.ui.progress_label import ProgressLabel
from src.client.ui.shadow.tk.nodes import TK
from src.client.ui.shadow.tk.widgets.widget import WidgetComponent
from src.client.ui.values.font import Font
from src.client.ui.volume_label import VolumeLabel
from src.client.volume import VolumeInfo
from src.now_playing import MediaStatus


def truncate_text(text: str, max_length: int) -> str:
    if len(text) > max_length:
        return text[: max_length - 1] + "⋯"
    return text


@dataclass
class MediaDisplay(WidgetComponent):
    status: MediaStatus

    def render(self):
        status = self.status
        yield TK.Label(
            background="#000001",
            ipadx=15,
            fill="both",
            foreground="#ffffff",
            font=Font(
                family="Segoe UI Emoji",
                size=18,
                style="normal",
            ),
            text=truncate_text(status.title, 28),
        )
        yield TK.Label(
            background="#000001",
            ipadx=15,
            fill="both",
            foreground="#aaaafb",
            font=Font(
                family="Segoe UI Emoji",
                size=15,
                style="normal",
            ),
            text=truncate_text(status.artist, 28),
        )
        yield ProgressLabel(
            duration=status.duration,
            position=status.position,
            is_playing=status.is_playing,
        )
        yield VolumeLabel(volume=status.volume)
