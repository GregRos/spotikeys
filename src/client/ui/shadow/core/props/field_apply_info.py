from dataclasses import dataclass, field
from typing import Any, Callable, Literal


@dataclass(frozen=True)
class FieldApplyInfo[X]:
    type: str
    converter: Callable[[X], Any] | None = field(default=None)
    diff: bool = field(default=True)
