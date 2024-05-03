from dataclasses import field
from tkinter import Label, Widget
from typing import Any, Callable, Literal, override
from attr import dataclass

from src.client.ui.framework.make_clickthrough import make_clickthrough
from src.client.ui.shadow.core.base import ShadowNode, ShadowTkWidget
from src.client.ui.shadow.core.fields import configure_field, pack_field
from src.client.ui.values.font import Font


class TK:
    @dataclass()
    class Label(ShadowTkWidget):

        @property
        @override
        def tk_type(self) -> str:
            return "Label"

        text: str = configure_field(default=" ")
        font: Font = configure_field(
            Font("Courier New", 18, "normal"), converter=lambda x: x.to_tk()
        )
        ipadx: int = pack_field(default=0)
        ipady: int = pack_field(default=0)
        fill: Literal["both", "x", "y", "none"] = pack_field(default="none")
        background: str = configure_field(default="#000001")
        foreground: str = configure_field(default="#ffffff")
        justify: str = configure_field(default="center")
        relief: str = configure_field(default="solid")
        borderwidth: int = configure_field(default=0)
