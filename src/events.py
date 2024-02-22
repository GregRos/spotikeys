from src.commands import Command
from ui.floating_tooltip import FloatingTooltip


class Executor:
    _tt: FloatingTooltip

    def __init__(self):
        self._tt = FloatingTooltip()
        self._tt.start()

    def action(self, action: Command):
        self._tt.set_text("Action", action.code)
        self._tt.show((-200, -200))

        self._tt.hide()
