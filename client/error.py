from dataclasses import dataclass
from math import trunc
from client.media.command_header import MediaCommandHeader
from src.kb.triggered_command import FailedCommand, OkayCommand
from src.ui.model.component import (
    Component,
)
from client.media.progress_label import ProgressLabel
from src.ui import Label, Component, Font, Widget
from client.media.volume_label import VolumeLabel
from client.media.volume import VolumeInfo
from src.spotify.now_playing import MediaStatus


def find_message(exc: Exception) -> str:
    return next(x for x in exc.args if isinstance(x, str))


@dataclass
class FailDisplay(Component[Widget]):
    executed: FailedCommand

    def render(self, yld, _):
        executed = self.executed
        error_name = executed.exception.__class__.__name__
        yld(
            Label(
                background="#000001",
                foreground="#ff0000",
                font=Font(
                    family="Segoe UI Emoji",
                    size=18,
                    style="bold",
                ),
                text=f"{error_name}",
            ).Pack(
                ipadx=15,
                fill="both",
            )
        )
        for x in executed.exception.args:
            if isinstance(x, tuple):
                continue
            yld(
                Label(
                    background="#000001",
                    foreground="#ff0000",
                    font=Font(
                        family="Segoe UI Emoji",
                        size=14,
                        style="italic",
                    ),
                    wraplength=380,
                    text=str(x),
                ).Pack(
                    ipadx=15,
                    fill="both",
                )
            )
