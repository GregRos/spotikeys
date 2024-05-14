from dataclasses import dataclass
from math import trunc
from typing import Generator, override
from src.client.ui.shadow.core.rendering.component import Component
from src.client.ui.shadow.core.reconciler.shadow_node import ShadowProps
from src.client.ui.shadow.tk.nodes import TK
from src.client.ui.shadow.tk.widgets.widget import WidgetNode, WidgetComponent
from src.client.ui.values.font import Font
from src.client.volume import VolumeInfo


@dataclass
class VolumeLabel(WidgetComponent):
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
    def render(self):
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
