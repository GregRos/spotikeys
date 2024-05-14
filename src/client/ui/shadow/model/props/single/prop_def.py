from src.client.ui.shadow.model.props.operators import SAME, Computable, Diffable
from src.client.ui.shadow.model.props.single.prop_value import PropValue


from pydantic import Field
from pydantic.dataclasses import dataclass


from copy import copy
from typing import Any, Callable, Literal, Self, cast, override

DiffMode = Literal["simple", "recursive", "never"]


@dataclass(kw_only=True)
class PropDef[X](Computable, Diffable):
    diff_mode: DiffMode = Field(default="recursive")
    section: str = Field(default=None)
    alias: str = Field(default=None)
    default: X = Field(default=None)
    converter: Callable[[X], Any] = Field(default=None)
    value_type: type[X] = Field(default=None)

    @override
    def delta_from(self, other: Self) -> Any:
        return self if self != other else SAME

    def set(self, **kwargs: Any) -> "PropDef[X]":
        return copy(self, **kwargs)

    def transform(self, key: str, value: Any) -> tuple[str, Any]:
        return (self.alias or key, self.converter(value) if self.converter else value)

    def __bool__(self) -> bool:
        return False

    def wrap[Y](self, value: Y) -> "PropValue[Y]":
        return PropValue[Y](value, cast(PropDef[Y], self))

    def merge(self, other: "PropDef[X]") -> "PropDef[X]":
        return self.set(**{k: v for k, v in other.__dict__.items() if v is not None})

    def compute(self, key: str) -> tuple[str, Any] | None:
        return self.alias if self.alias else key, self.default
