from typing import Callable, Generator
from src.client.ui.framework.component import Component


from tkinter import Widget

from src.client.ui.shadow.core.base import ShadowNode


def render_recursively[
    Props: object
](component: Component[Props]) -> Generator[ShadowNode[Widget], None, None]:
    for child in component.render():
        if isinstance(child, Component):
            yield from render_recursively(child)
        else:
            yield child


class Renderer:
    _last_render: list[Widget]

    def __init__(self, target: Component):
        self.target = target
        self._last_render = []

    before_render: Callable[[], None] | None = None

    def render(self):
        if self.before_render:
            self.before_render()
        this_render = [*render_recursively(self.target)]
        last = self._last_render
        i = 0
        j = 0
        while i < len(last) and j < len(this_render):
            if last[i] != this_render[j]:
                last[i].pack_forget()
                this_render[j].pack()
            i += 1
            j += 1

        if i < len(last):
            for k in range(i, len(last)):
                last[k].pack_forget()

        if j < len(this_render):
            for k in range(j, len(this_render)):
                this_render[k].pack()
