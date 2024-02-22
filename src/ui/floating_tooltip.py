from tkinter import Tk, Label, SOLID, LEFT, CENTER
from typing import Tuple

from src.ui.make_clickthrough import make_clickthrough


class FloatingTooltip:
    _tk: Tk
    _title: Label
    _body: Label
    _pos: Tuple[int, int]

    def __init__(self):
        tk = self._tk = Tk()
        tk.attributes('-topmost', 1, "-transparentcolor", "white")
        tk.wm_attributes("-topmost", True)
        tk.config(bg='white')
        tk.overrideredirect(True)
        self._title = title = (
            Label(tk, text="xd", justify=CENTER,
                  relief=SOLID, borderwidth=0,
                  foreground="#000000",
                  font=("Segoe UI", "18", "bold")))

        self._body = body = (
            Label(tk, text="xd", justify=LEFT,
                  relief=SOLID, borderwidth=0,
                  foreground="#000000",
                  font=("Segoe UI", "14", "normal")))

    def _normalize_pos(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        pos_x, pos_y = pos
        screen_width = self._tk.winfo_screenwidth()
        screen_height = self._tk.winfo_screenheight()
        if pos_x < 0:
            pos_x = screen_width + pos_x
        if pos_y < 0:
            pos_y = screen_height + pos_y
        return pos_x, pos_y

    def set_position(self, pos: Tuple[int, int]):
        pos = self._normalize_pos(pos)
        self._pos = pos
        self._tk.wm_geometry("+%d+%d" % pos)

    def set_text(self, title: str, body: str):
        self._title.config(text=title)
        self._body.config(text=body)

    def show(self, pos: Tuple[int, int] = None):
        if pos is None:
            pos = self._pos
        pos = self._normalize_pos(pos)
        title = self._title
        body = self._body
        self._tk.wm_geometry("+%d+%d" % pos)
        title.place(x=0, y=0, width=200)
        body.place(x=0, y=100, width=200)
        title.pack(ipadx=15, fill="x", expand=True)
        body.pack(ipadx=15, fill="x", expand=True)
        make_clickthrough(title)
        make_clickthrough(body)
        self._pos = pos
        self._tk.update_idletasks()

    def hide(self):
        self._title.pack_forget()
        self._body.pack_forget()
        self._tk.update_idletasks()

    def start(self):
        self._tk.update()
