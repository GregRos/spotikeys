from abc import abstractmethod
from dataclasses import dataclass
from itertools import groupby
from tkinter import Label, Tk, Widget
from types import MappingProxyType
from typing import TYPE_CHECKING, Callable, Generator, Literal, Self, override
from pyrsistent import m, pmap
from src.client.ui.framework.component import Component
from src.client.ui.framework.make_clickthrough import make_clickthrough


from src.client.ui.shadow.core.props.props_map import DiffMap
from src.client.ui.shadow.core.props.shadow_node import ShadowNode


@dataclass(kw_only=True)
class SwTkWidget(ShadowNode, groups={"configure": "recursive", "pack": "unit"}):

    def __init_subclass__(cls):
        pass

    @property
    @abstractmethod
    def tk_type(self) -> str: ...
