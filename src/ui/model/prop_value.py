from dataclasses import dataclass, field
from src.ui.model.prop_def import Prop


from typing import Any, TypeGuard, override


class PropValue:
    __match_args__ = ("value", "prop")

    def __init__(self, prop: Prop, value: Any) -> None:
        self.prop = prop
        self.value = value

    def compute(self, key: str) -> tuple[str, Any]:
        v = self.value or self.prop.default
        v = self.prop.converter(v) if self.prop.converter else v
        k = self.prop.alias or key
        return k, v
