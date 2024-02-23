from threading import Thread
from tkinter import Tk
from typing import Callable

from commanding import ReceivedCommand
from ui.commands import UiCommand
from ui.floating_tooltip import MediaTooltip


class ActivityDisplay:
    _thread: Thread
    _tk: Tk
    _tooltip: MediaTooltip
    _last_ui_command: object

    def __init__(self):
        def ui_thread():
            self._tk = Tk()
            self._tooltip = MediaTooltip(self._tk)
            self._tk.mainloop()

        self._thread = Thread(target=ui_thread)

    def command_start(self, command: ReceivedCommand):
        def start_timeout():

        self._last_ui_command = command
        self._tk.after(0, self._tooltip.command_sent, command)


    def start(self):
        self._thread.start()

    def execute(self, func: Callable[[MediaTooltip], None], elapsed: int = 0):
        self._tk.after(0, func, self._tooltip)
