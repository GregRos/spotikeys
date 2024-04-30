from __future__ import annotations
import abc
from tkinter import Tk, Widget
from typing import TYPE_CHECKING, Any, Generator, Tuple, TypedDict, Unpack, override

from attr import frozen

from src.client.ui.binding.active_value import ActiveValue
from src.client.ui.shadow.core.base import ShadowNode

if TYPE_CHECKING:
    from src.client.ui.framework.tooltip_row import TooltipRow


class Component(abc.ABC):

    @abc.abstractmethod
    def render(self) -> Generator[ShadowNode | Component, None, None]: ...
