from tkinter import Tk
from typing import Literal, Tuple, TypedDict

from src.ui.model.shadow_node import InitPropsBase

type AnchorType = Literal["lt", "rt", "lb", "rb"]


class Geometry(InitPropsBase):
    anchor_point: AnchorType
    width: int
    height: int
    x: int
    y: int
