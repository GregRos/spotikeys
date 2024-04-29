from threading import Thread
import threading
from time import sleep
from tkinter import Tk

from src.client.ui.framework.active_value import ActiveValue


class UiOwner[Value]:
    _tk: Tk
    _thread: Thread

    def __init__(self):
        from src.client.ui.tooltip_row import TooltipRow

        owner = self
        self.value = ActiveValue[Value](
            "value", scheduler=lambda f: self._tk.after(0, f)
        )

        class TT(TooltipRow):
            def __init__(self):
                super().__init__(owner)

            def __post_init__(self):
                self._parent = owner

            pass

        waiter = threading.Event()

        def ui_thread():
            self._tk = Tk()
            waiter.set()
            self._tk.mainloop()

        self._thread = Thread(target=ui_thread)
        self._thread.start()
        waiter.wait()
        self._ToolTipRow = TT

    def auto_hide_after(self, time: float, value: Value):

        def on_timeout():
            sleep(time)
            if self.value._last_value == value:
                self.hide()

        Thread(target=on_timeout).start()

    def hide(self):
        self._tk.after(0, self._tk.withdraw)
