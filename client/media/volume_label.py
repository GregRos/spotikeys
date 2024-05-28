from dataclasses import dataclass
from math import trunc
from typing import Generator, override
from src.ui.model.component import Component
from src.ui.model.shadow_node import ShadowProps
from src.ui import Label, Widget, Component, Window
from src.ui.tk.font import Font
from client.media.volume import VolumeInfo


@dataclass
class VolumeLabel(Component[Widget]):
    volume: VolumeInfo

    def get_volume_line(self):
        info = self.volume
        empty = "◇"
        full = "◇" if info.mute else "◆"
        if info.mute:
            return f"🔇 {empty * 16}"
        full_boxes = trunc(info.volume / 100 * 16)
        return f"🔊 {full * full_boxes}{empty * (16 - full_boxes)}"

    @override
    def render(self, yld, _):
        yld(
            Label(
                text=self.get_volume_line(),
                background="#000001",
                foreground="#00ff00",
                font=Font(
                    family="Segoe UI Emoji",
                    size=13,
                    style="normal",
                ),
            ).Pack(
                ipadx=40,
                ipady=13,
                fill="both",
            )
        )
