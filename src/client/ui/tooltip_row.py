from __future__ import annotations
import inspect
from tkinter import CENTER, SOLID, Label, Tk

from typing import TYPE_CHECKING, Any, Callable, Literal, Optional, TypeGuard

from src.client.ui.framework.bindable_property import bindable
from src.client.ui.framework.lbl import UiOwner

if TYPE_CHECKING:
    from tkinter.font import _FontDescription


class TooltipRow:
    _label: Label
    _ipadx: int
    _ipady: int
    _fill: Literal["both", "x", "y", "none"]
    _parent: UiOwner
    _font: tuple[str, int, str]

    def unplace(self):
        self._label.pack_forget()

    def __init__(
        self,
        parent: UiOwner,
        *,
        y: int = 0,
        x: int = 0,
        ipadx: int = 0,
        ipady: int = 0,
        text: str = " ",
        fill: Literal["both", "x", "y", "none"] = "none",
        font: tuple[str, int, str] = ("Segoe UI Emoji", 12, "normal"),
        bg: str = "#000000",
        fg: str = "#ffffff",
    ):
        self._parentTk = parent
        self._ipadx = ipadx
        self._ipady = ipady
        self._fill = fill
        self._font = font
        self._y = y
        self._x = x
        self._label = Label(
            parent._tk,
            text=text,
            justify=CENTER,
            relief=SOLID,
            borderwidth=0,
            background=bg,
            foreground=fg,
            font=font,
        )

    @bindable()
    def ipadx(self, value: int):
        self._ipadx = value
        return self

    @bindable()
    def ipady(self, value: int):
        self._ipady = value
        return self

    @bindable()
    def fill(self, value: Literal["both", "x", "y", "none"]):
        self._fill = value
        return self

    @bindable()
    def font_size(self, value: int):

        self._label.configure(font=(self._font[0], value, self._font[2]))
        return self

    @bindable()
    def placed(self, value: bool):
        if value:
            self.place()
        else:
            self.unplace()
        return self

    @bindable()
    def font(self, value: tuple[str, int, str]):
        self._label.configure(font=value)
        return self

    @bindable()
    def background(self, value: str):
        self._label.configure(bg=value)
        return self

    @bindable()
    def foreground(self, value: str):
        self._label.configure(foreground=value)
        return self

    @bindable()
    def text(self, value: str):
        self._label.configure(text=value)
        return self

    @bindable()
    def y(self, value: int):
        self._y = value
        return self

    @bindable()
    def x(self, value: int):
        self._x = value
        return self

    def place(self):
        self._label.place()
        self._label.pack(ipadx=self._ipadx, ipady=self._ipady, fill=self._fill)


def is_two_param_callable(obj) -> TypeGuard[Callable[[Any, TooltipRow], str]]:
    return callable(obj) and len(inspect.signature(obj).parameters) == 2
