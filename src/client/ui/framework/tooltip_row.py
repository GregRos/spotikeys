from __future__ import annotations
import inspect
from tkinter import CENTER, SOLID, Label, Tk, Widget

from typing import TYPE_CHECKING, Any, Callable, Literal, Optional, TypeGuard, override

from src.client.ui.binding.bindable import bindable
from src.client.ui.shadow.component import Component
from src.client.ui.framework.owner import UiRoot

if TYPE_CHECKING:
    from tkinter.font import _FontDescription


class TooltipRow(Component):
    _label: Label
    _ipadx: int = 0
    _ipady: int = 0
    _fill: Literal["both", "x", "y", "none"] = "none"
    _font_family: str = "Courier New"
    _font_size: int = 18
    _font_style: str = "normal"

    def unplace(self):
        self._label.configure())
        self._label.pack_forget()

    def __init__(self, parent: Component):
        super().__init__(parent)
        self._parentTk = parent

        self._label = Label(
            parent.tk, justify=CENTER, relief=SOLID, borderwidth=0, text=" "
        )

    def render(self):
        yield self._label

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

    def _get_font(self) -> _FontDescription:
        return (self._font_family, self._font_size, self._font_style)

    @bindable()
    def wrap_width(self, width: int):
        self._label.configure(wraplength=width)
        return self

    @bindable()
    def wrap(self, value: bool):
        self._label.configure(wraplength=0)
        return self

    @bindable()
    def font_size(self, value: int):
        self._font_size = value
        self._label.configure(font=self._get_font())
        return self

    @bindable()
    def font_family(self, value: str):
        self._font_family = value
        self._label.configure(font=self._get_font())
        return self

    @bindable()
    def font_style(self, value: str):
        self._font_style = value
        self._label.configure(font=self._get_font())
        return self

    @bindable()
    def placed(self, value: bool):
        if value:
            self.place()
        else:
            self.unplace()
        return self

    @bindable(only_changed=False)
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
        self._label.pack(
            ipadx=self._ipadx,
            ipady=self._ipady,
            fill=self._fill,
        )


def is_two_param_callable(obj) -> TypeGuard[Callable[[Any, TooltipRow], str]]:
    return callable(obj) and len(inspect.signature(obj).parameters) == 2
