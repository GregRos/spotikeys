from dataclasses import dataclass
from typing import Literal, TypedDict, override

from client.media_types import MediaStageMessage
from src.kb.triggered_command import FailedCommand, OkayCommand, TriggeredCommand
from src.ui.model.component import Component
from src.ui.tk.widget import Label
from src.ui.tk.font import Font


CommandTypes = Literal["status", "trigger", "okay", "failed"]


@dataclass
class CommandHeader(Component):
    input: MediaStageMessage
    justify: int
    colors: dict[CommandTypes, str]

    def get_color(self):
        match self.input:
            case x if x.command.code == "show_status":
                return self.colors["status"]
            case FailedCommand():
                return self.colors["failed"]
            case TriggeredCommand():
                return self.colors["trigger"]

            case OkayCommand():
                return self.colors["okay"]

    def get_text(self):
        match self.input:
            case FailedCommand(triggered):
                return f"{str(triggered.command).ljust(self.justify)} {self.input.duration * 1000.:.0f}ms"
            case TriggeredCommand(code):
                return (
                    f"{str(code).ljust(self.justify)} ⌛⌛"
                    if code != "show_status"
                    else f"{str(code).ljust(self.justify)} ⌛⌛"
                )
            case OkayCommand(triggered) as c:
                return (
                    f"{str(triggered.command).ljust(self.justify)} ⌛⌛"
                    if triggered.command.code == "show_status"
                    else f"{triggered.command.__str__().ljust(self.justify)} {c.duration * 1000:.0f}ms"
                )

    @override
    def render(self, yld, _):
        yld(
            Label(
                text=self.get_text(),
                background=self.get_color(),
                foreground="#dddddd",
                font=Font(
                    family="Segoe UI Emoji",
                    size=13,
                    style="bold",
                ),
            ).Pack(
                ipadx=20,
                ipady=5,
                fill="both",
            )
        )
