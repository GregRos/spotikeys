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


@dataclass
class FailDisplay(Component[Widget]):
    executed: FailedCommand

    def render(self, yld, _):
        executed = self.executed

        yld(
            Label(
                background="#000001",
                foreground="#ff0000",
                font=Font(
                    family="Segoe UI Emoji",
                    size=18,
                    style="normal",
                ),
                wraplength=380,
                text=executed.exception.args[0],
            ).Pack(
                ipadx=15,
                fill="both",
            )
        )
