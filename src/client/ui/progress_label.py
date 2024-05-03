from dataclasses import dataclass
from typing import Generator, override
from src.client.ui.framework.component import Component
from src.client.ui.shadow.core.props.shadow_node import ShadowNode
from src.client.ui.shadow.tk.nodes import TK
from src.client.ui.values.font import Font
from src.now_playing import MediaStatus


def format_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{int(minutes):02d}:{int(seconds):02d}"




    return progress_line

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
@dataclass()        
class ProgressLabel(Component):
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