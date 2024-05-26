from dataclasses import dataclass, field
from src.ui.model.prop import Prop


from typing import Any, TypeGuard, override


def format_value(value: Any) -> str:
    if isinstance(value, str):
        return f'"{value}"'
    return str(value)


class PValue:
    __match_args__ = ("value", "prop")

    def __init__(self, prop: Prop, value: Any) -> None:
        self.prop = prop
        self.value = value

    def __repr__(self) -> str:
        return f"{self.prop.name}={format_value(self.value)}"

    def compute(self) -> tuple[str, Any]:
        v = self.value or self.prop.no_value
        v = self.prop.converter(v) if self.prop.converter else v
        k = self.prop.name or ""
        return k, v

    def __eq__(self, other: Any) -> bool:
        return (
            isinstance(other, PValue)
            and self.prop == other.prop
            and self.value == other.value
        )
