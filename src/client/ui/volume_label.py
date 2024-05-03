from dataclasses import dataclass
from math import trunc
from typing import Generator, override
from src.client.ui.framework.component import Component
from src.client.ui.shadow.core.props.shadow_node import ShadowNode
from src.client.ui.shadow.tk.nodes import TK
from src.client.ui.values.font import Font
from src.client.volume import VolumeInfo


@dataclass
class VolumeLabel(Component):
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
    def render(self) -> Generator[ShadowNode | Component, None, None]:
        yield TK.Label(
            text=self.get_volume_line(),
            background="#000001",
            foreground="#00ff00",
            font=Font(
                family="Segoe UI Emoji",
                size=13,
                style="normal",
            ),
            ipadx=40,
            ipady=13,
            fill="both",
        )
