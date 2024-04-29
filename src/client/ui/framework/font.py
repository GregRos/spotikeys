from dataclasses import dataclass, field

from src.client.ui.framework.active_value import ActiveValue
from src.client.ui.framework.bindable_property import bindable


@dataclass
class FontInfo:
    family: str = "Courier New"
    size: int = 18
    style: str = "normal"

    def to_tk(self):
        return (self.family, self.size, self.style)


class Font(ActiveValue):
    _family: str = "Courier New"
    _size: int = 18
    _style: str = "normal"

    @bindable()
    def family(self, value: str):
        self._family = value
        return self

    @bindable()
    def size(self, value: int):
        self._size = value
        return self

    @bindable()
    def style(self, value: str):
        self._style = value
        return self

    def value(self):
        return self.family
