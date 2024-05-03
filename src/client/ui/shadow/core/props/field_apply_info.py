from dataclasses import dataclass, field
from typing import Any, Callable


@dataclass(frozen=True)
class FieldApplyInfo[X]:
    type: str
    converter: Callable[[X], Any] | None = field(default=None)
