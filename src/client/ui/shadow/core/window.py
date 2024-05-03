from dataclasses import dataclass, field
from tkinter import Tk
from typing import override

from src.client.ui.framework.make_clickthrough import make_clickthrough
from src.client.ui.shadow.core.base import ShadowBase
from src.client.ui.values.geometry import Geometry


@dataclass(kw_only=True)
class ShadowWindow(ShadowBase[Tk]):
    geometry: Geometry
    topmost: bool = field(default=False)
    transparent_color: str | None = field(default=None)
    override_redirect: bool = field(default=False)
    visible: bool = field(default=True)
