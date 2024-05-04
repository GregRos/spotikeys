from dataclasses import dataclass, field
from itertools import zip_longest


from tkinter import Label, Tk, Widget
from typing import TYPE_CHECKING, Any, Callable, Generator, Literal, final, override


from src.client.ui.framework.make_clickthrough import make_clickthrough

from src.client.ui.shadow.core.props.shadow_node import ShadowNode
from src.client.ui.shadow.tk.widgets.widget import SwTkWidget
