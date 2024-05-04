from dataclasses import dataclass, field
from typing import Any, Callable, Literal


@dataclass(frozen=True)
class PropInfo[X]:
    type: str
    name: str | None = field(default=None)
    converter: Callable[[X], Any] | None = field(default=None)
