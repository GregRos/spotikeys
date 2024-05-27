from dataclasses import dataclass
from math import trunc
from src.kb.triggered_command import OkayCommand
from src.ui.model.component import (
    Component,
)
from src.client.progress_label import ProgressLabel
from src.ui import Label, Component, Font, Widget
from src.client.volume_label import VolumeLabel
from src.client.volume import VolumeInfo
from src.now_playing import MediaStatus


def truncate_text(text: str, max_length: int) -> str:
    if len(text) > max_length:
        return text[: max_length - 1] + "⋯"
    return text


@dataclass
class MediaDisplay(Component[Widget]):
    status: MediaStatus

    def render(self, yld, _):
        status = self.status
        yld(
            Label(
                background="#000001",
                foreground="#ffffff",
                font=Font(
                    family="Segoe UI Emoji",
                    size=18,
                    style="normal",
                ),
                text=truncate_text(status.title, 28),
            ).Pack(
                ipadx=15,
                fill="both",
            )
        )
        yld(
            Label(
                background="#000001",
                foreground="#aaaafb",
                font=Font(
                    family="Segoe UI Emoji",
                    size=15,
                    style="normal",
                ),
                text=truncate_text(status.artist, 28),
            ).Pack(
                ipadx=15,
                fill="both",
            )
        )
        yld(
            ProgressLabel(
                duration=status.duration,
                position=status.position,
                is_playing=status.is_playing,
            )
        )
        yld(VolumeLabel(volume=status.volume))
