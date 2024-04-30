from threading import Thread
import threading
from time import sleep
from tkinter import Tk, Widget
from typing import TYPE_CHECKING, Generator, Tuple

from src.client.ui.binding.active_value import ActiveValue
from src.client.ui.values.geometry import Geometry
from src.client.ui.framework.renderer import Renderer

if TYPE_CHECKING:
    from src.client.ui.framework.tooltip_row import Component


class UiRoot[X: Component]:
    _tk: Tk
    _thread: Thread
    _renderer: Renderer | None = None
    root: X

    @property
    def tk(self) -> Tk:
        return self._tk

    def __init__(self, geometry: Geometry):
        self.geometry = geometry

        waiter = threading.Event()

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

    def mount[
        Z: Component
    ](self, component_class: type[Z], *args, **kwargs) -> "UiRoot[Z]":
        cmp = component_class(self.tk, *args, **kwargs)
        if self._renderer:
            self._renderer.close()
        self._renderer = Renderer(cmp)
        self.root = cmp  # type: ignore
        return self  # type: ignore

    def place(self):
        self._tk.wm_geometry(self.geometry.normalize(self.tk).to_tk())
        self._tk.deiconify()
        if not self._renderer:
            raise ValueError("No component mounted")

        self._renderer.render()

    def unplace(self):
        self._tk.after(0, self._tk.withdraw)

    def hide(self):
        self._tk.withdraw()
