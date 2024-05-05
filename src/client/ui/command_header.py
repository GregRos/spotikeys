from dataclasses import dataclass
from typing import Literal, override

from src.client.kb.triggered_command import FailedCommand, OkayCommand, TriggeredCommand
from src.client.ui.floating_tooltip import MediaStageMessage
from src.client.ui.shadow.core.rendering.component import Component
from src.client.ui.shadow.tk.nodes import TK
from src.client.ui.values.font import Font


CommandTypes = Literal["status", "trigger", "okay"]


@dataclass
class CommandHeader(Component):
    input: MediaStageMessage
    justify: int
    colors: dict[CommandTypes, str]

    def get_color(self):
        match self.input:
            case FailedCommand():
                return self.colors["status"]
            case TriggeredCommand():
                return self.colors["trigger"]
            case OkayCommand():
                return self.colors["okay"]

    def get_text(self):
        match self.input:
            case FailedCommand(triggered):
                return f"❌ {str(triggered).ljust(self.justify)} {self.input.duration * 1000:.0f}ms"
            case TriggeredCommand(code):
                return (
                    f"⌛ {str(code).ljust(self.justify)} ⌛⌛"
                    if code != "show_status"
                    else f"💡 {str(code).ljust(self.justify)} ⌛⌛"
                )
            case OkayCommand(triggered) as c:
                return (
                    f"💡 {str(triggered).ljust(self.justify)} ⌛⌛"
                    if triggered.command.code == "show_status"
                    else f"✅ {triggered.__str__().ljust(self.justify)} {c.duration * 1000:.0f}ms"
                )

    @override
    def render(self, state):
        yield TK.Label(
            text=self.get_text(),
            background=self.get_color(),
            foreground="#dddddd",
            font=Font(
                family="Segoe UI Emoji",
                size=12,
                style="normal",
            ),
            ipadx=20,
            ipady=5,
            fill="both",
        )
