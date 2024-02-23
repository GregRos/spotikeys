from threading import Thread
from tkinter import Tk
from typing import Callable

from src.ui.floating_tooltip import FloatingTooltip


class UiThread:
    _thread: Thread
    _tk: Tk
    _tooltip: FloatingTooltip
    _last_event: Callable[[FloatingTooltip], None]

    def __init__(self):
        def ui_thread():
            self._tk = Tk()
            self._tooltip = FloatingTooltip(self._tk)
            self._tk.mainloop()

        self._thread = Thread(target=ui_thread)

    def start(self):
        self._thread.start()

    def execute(self, func: Callable[[FloatingTooltip], None], elapsed: int = 0):
        self._tk.after(0, func, self._tooltip)
