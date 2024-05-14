from dataclasses import dataclass
from typing import Generator, override
from src.client.ui.shadow.core.rendering.component import Component
from src.client.ui.shadow.core.reconciler.shadow_node import ShadowProps
from src.client.ui.shadow.tk.nodes import TK
from src.client.ui.shadow.tk.widgets.widget import WidgetComponent
from src.client.ui.values.font import Font
from src.now_playing import MediaStatus


def format_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{int(minutes):02d}:{int(seconds):02d}"


@dataclass()
class ProgressLabel(WidgetComponent):
    duration: float
    position: float
    is_playing: bool

    @property
    def progress(self):
        return round(100 * self.position / self.duration)

    @override
    def render(self):
        yield TK.Label(
            text=self.get_progress_line(),
            background="#000001",
            foreground="#ffffff",
            font=Font(
                family="Segoe UI Emoji",
                size=14,
                style="normal",
            ),
            ipadx=20,
            ipady=15,
            fill="both",
        )

    def get_progress_line(self):
        remaining_time = format_duration(self.duration - self.position)
        full_blocks = round(float(self.progress / 100) * 9)
        progress_line = f"{ '▶' if self.is_playing else '⏸' } {'█' * full_blocks}{'░' * (9 - full_blocks)} {remaining_time}"
        return progress_line
