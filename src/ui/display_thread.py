from threading import Thread
from time import sleep
from tkinter import Tk
from typing import Callable

from commanding import ReceivedCommand
from ui.floating_tooltip import MediaTooltip


class ActivityDisplay:
    _thread: Thread
    _tk: Tk
    _tooltip: MediaTooltip
    _last_ui_action: object

    def __init__(self):
        def ui_thread():
            self._tk = Tk()
            self._tooltip = MediaTooltip(self._tk)
            self._tk.mainloop()

        self._thread = Thread(target=ui_thread)
        self._thread.start()

    def add_auto_hide_timer(self, obj: object):
        def on_timeout():
            sleep(3)
            if self._last_ui_action == obj:
                self._tk.after(0, self._tooltip.hide)

        Thread(target=on_timeout).start()

    def run(self, action: Callable[[MediaTooltip], None]):
        self._last_ui_action = action
        self._tk.after(0, action, self._tooltip)
        self.add_auto_hide_timer(action)
