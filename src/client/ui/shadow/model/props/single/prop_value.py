from dataclasses import dataclass, field
from src.client.ui.shadow.model.props.single.prop_def import PropDef


from typing import Any, TypeGuard, override


class PropValue:
    __match_args__ = ("value", "prop")

    def __init__(self, prop: PropDef, value: Any) -> None:
        self.prop = prop
        self.value = value

    def compute(self, key: str) -> tuple[str, Any]:
        v = self.value or self.prop.default
        v = self.prop.converter(v) if self.prop.converter else v
        k = self.prop.alias or key
        return k, v
