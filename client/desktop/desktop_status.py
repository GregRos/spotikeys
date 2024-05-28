from dataclasses import dataclass, field

from src.kb.triggered_command import TriggeredCommand
from pyvda import VirtualDesktop, AppView
from win32gui import GetWindowText


class DesktopAction:
    pass


class Desk:
    pos: int
    name: str

    def __init__(self, vd: VirtualDesktop):
        self.pos = vd.number
        self.name = vd.name or f"Desktop {vd.number}"


class App:
    title: str
    hwnd: int

    def __init__(self, app_view: AppView):
        self.title = GetWindowText(app_view.hwnd)  # type: ignore
        self.hwnd = app_view.hwnd


class Pan(DesktopAction):
    start: Desk
    end: Desk

    def __init__(self, start: VirtualDesktop, end: VirtualDesktop):
        self.start = Desk(start)
        self.end = Desk(end)

    def from_command(self, cmd: TriggeredCommand, shove: "Shove | None" = None):
        return DesktopExec(cmd, pan=self, shove=shove)


class Shove(DesktopAction):
    def __init__(self, app_view: AppView, start: VirtualDesktop, end: VirtualDesktop):
        self.app = App(app_view)
        self.start = Desk(start)
        self.end = Desk(end)

    start: Desk
    end: Desk

    def from_command(self, cmd: TriggeredCommand, pan: "Pan | None" = None):
        return DesktopExec(cmd, pan=pan, shove=self)


@dataclass
class DesktopExec(DesktopAction):
    command: TriggeredCommand
    pan: Pan | None = field(default=None)
    shove: Shove | None = field(default=None)
