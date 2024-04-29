from threading import Thread
import threading
from time import sleep
from tkinter import Tk
from typing import Tuple

from src.client.ui.binding.active_value import ActiveValue


class UiRoot[Value]:
    _tk: Tk
    _thread: Thread

    def __init__(self, size: Tuple[int, int], pos: Tuple[int, int] = (0, 0)):
        from src.client.ui.framework.tooltip_row import TooltipRow

        self._size = size
        self._pos = pos
        owner = self
        self.value = ActiveValue[Value](
            "value", scheduler=lambda f: self._tk.after(0, f)
        )

        waiter = threading.Event()

        class TT(TooltipRow):
            def __init__(self):
                super().__init__(owner)

            def __post_init__(self):
                self._parent = owner

            pass

        def ui_thread():
            self._tk = Tk()
            waiter.set()
            self._tk.mainloop()

        self._thread = Thread(target=ui_thread)
        self._thread.start()
        waiter.wait()
        tk = self._tk
        tk.attributes("-topmost", 1, "-transparentcolor", "black")
        tk.wm_attributes("-topmost", True)
        tk.config(bg="black")
        tk.overrideredirect(True)
        self._ToolTipRow = TT

    def place_window(self, pos: Tuple[int, int]):
        pos = self._normalize_pos(pos)
        geometry = "".join(["%dx%d" % self._size, "+%d+%d" % pos])
        self._tk.wm_geometry(geometry)
        self._tk.deiconify()

    def _normalize_pos(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        pos_x, pos_y = pos
        screen_width = self._tk.winfo_screenwidth()
        screen_height = self._tk.winfo_screenheight()
        if pos_x < 0:
            pos_x = screen_width + pos_x
        if pos_y < 0:
            pos_y = screen_height + pos_y
        return pos_x, pos_y

    def auto_hide_after(self, time: float, value: Value):

        def on_timeout():
            sleep(time)
            if self.value._last_value == value:
                self.hide()

        Thread(target=on_timeout).start()

    def hide(self):
        self._tk.after(0, self._tk.withdraw)


class Component:
    @property
    def tk(self):
        return self._root._tk

    def __init__(self, root: UiRoot):
        from src.client.ui.framework.tooltip_row import TooltipRow

        self._root = root
        owner = self

        class TT(TooltipRow):
            def __init__(self):
                super().__init__(owner)

            def __post_init__(self):
                self._parent = owner

            pass

        self._owner = root
        self._ToolTipRow = TT
