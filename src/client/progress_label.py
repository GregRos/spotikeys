from dataclasses import dataclass
from typing import Generator, override
from src.ui import Component, Widget, Label, Font, Window


def format_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{int(minutes):02d}:{int(seconds):02d}"


@dataclass()
class ProgressLabel(Component[Widget]):
    duration: float
    position: float
    is_playing: bool

    @property
    def progress(self):
        return round(100 * self.position / self.duration)

    @override
    def render(self, _):
        yield Label(
            text=self.get_progress_line(),
            background="#000001",
            foreground="#ffffff",
            font=Font(
                family="Segoe UI Emoji",
                size=14,
                style="normal",
            ),
        ).pack(
            ipadx=20,
            ipady=15,
            fill="both",
        )

    def get_progress_line(self):
        remaining_time = format_duration(self.duration - self.position)
        full_blocks = round(float(self.progress / 100) * 9)
        progress_line = f"{ '▶' if self.is_playing else '⏸' } {'█' * full_blocks}{'░' * (9 - full_blocks)} {remaining_time}"
        return progress_line
