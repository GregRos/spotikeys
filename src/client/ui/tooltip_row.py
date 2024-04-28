from __future__ import annotations
import inspect
from tkinter import CENTER, SOLID, Label, Tk
from tkinter.font import _FontDescription
from typing import Any, Callable, Literal, Optional, TypeGuard


def is_two_param_callable(obj) -> TypeGuard[Callable[[Any, TooltipRow[Any]], str]]:
    return callable(obj) and len(inspect.signature(obj).parameters) == 2


class TooltipRow[Value]:
    _label: Label
    _ipadx: int
    _ipady: int
    _fill: Literal["both", "x", "y", "none"]
    _parent: Tk

    def unplace(self):
        self._label.pack_forget()

    def __init__(
        self,
        parent: Tk,
        projection: Callable[[Value, TooltipRow[Value]], str],
        *,
        ipadx: int = 0,
        ipady: int = 0,
        text: str = " ",
        fill: Literal["both", "x", "y", "none"] = "none",
        font: _FontDescription = ("Segoe UI Emoji", 12, "normal"),
        bg: str = "#000",
        fg: str = "#000",
    ):
        self._projection = projection
        self._parent = parent
        self._ipadx = ipadx
        self._ipady = ipady
        self._fill = fill
        self._label = Label(
            parent,
            text=text,
            justify=CENTER,
            relief=SOLID,
            borderwidth=0,
            background=bg,
            foreground=fg,
            font=font,
        )

    def ipadx(self, value):
        self._ipadx = value
        return self

    def ipady(self, value):
        self._ipady = value
        return self

    def fill(self, value):
        self._fill = value
        return self

    def font_size(self, value):
        self._label.configure(font=(self._label.cget("font"), value))
        return self

    def font(self, value: _FontDescription):
        self._label.configure(font=value)
        return self

    def background(self, value):
        self._label.configure(background=value)
        return self

    def foreground(self, value):
        self._label.configure(foreground=value)
        return self

    def text(self, value):
        self._label.configure(text=value)
        return self

    def place(self):
        self._label.place()
        self._label.pack(ipadx=self._ipadx, ipady=self._ipady, fill=self._fill)

    def value(self, obj):
        return self.text(self._projection(obj, self))
