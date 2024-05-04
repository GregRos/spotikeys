from dataclasses import dataclass, field
from typing import Any, Callable, Literal


@dataclass(frozen=True)
class FieldApplyInfo[X]:
    type: str
    name: str | None = field(default=None)
    converter: Callable[[X], Any] | None = field(default=None)
    diff: bool = field(default=True)
