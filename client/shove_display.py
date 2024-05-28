from dataclasses import dataclass
from client.desktop.desktop_status import Pan, Shove
from client.media.media_display import truncate_text
from src.ui import Component
from ui.tk.font import Font
from ui.tk.widget import Label


@dataclass
class ShoveDisplay(Component):
    shove: Shove

    def render(self, yld, _):
        yld(
            Label(
                text=truncate_text(f"📅 {self.shove.app.title}", 20),
                background="darkblue",
                foreground="white",
                font=Font(family="Segoe UI Emoji", size=12),
            ).Pack(
                ipadx=20,
                ipady=5,
                fill="both",
            )
        )
        yld(
            Label(
                text=truncate_text(f"🫸 {self.shove.start.name}", 20),
                background="darkblue",
                foreground="white",
                font=Font(
                    family="Segoe UI Emoji",
                    size=14,
                    style="bold",
                ),
            ).Pack(
                ipadx=20,
                ipady=5,
                fill="both",
            )
        )


@dataclass
class PanDisplay(Component):
    pan: Pan

    def render(self, yld, _):
        yld(
            Label(
                text=truncate_text(f"👁️ {self.pan.end.name}", 20),
                background="darkblue",
                foreground="white",
                font=Font(
                    family="Segoe UI Emoji",
                    size=14,
                    style="bold",
                ),
            ).Pack(
                ipadx=20,
                ipady=5,
                fill="both",
            )
        )
