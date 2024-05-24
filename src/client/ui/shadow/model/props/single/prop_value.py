from dataclasses import dataclass
from src.client.ui.shadow.model.props.single.prop_def import PropDef
from src.client.ui.shadow.model.props.operators import SAME, Computable, Diffable, diff
from src.client.ui.shadow.model.props.single.just_value import JustValue


from pydantic import Field


from typing import Any, TypeGuard, override


@dataclass(kw_only=True)
class PropValue[X]:
    __match_args__ = ("value", "prop")
    _cached: tuple[str, X] | None = Field(default=None)

    def __init__(self, value: X, prop: PropDef[X]):
        self._value = value
        self.prop = prop
        self._cached = None

    @property
    def value_type(self) -> type[X]:
        return self.prop.value_type

    @property
    def value(self) -> X:
        if self._value is not None:
            return self._value
        if self.prop.default is not None:
            return self.prop.default
        raise ValueError("No value set")

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, PropValue)
            and self._value == other._value
            and self.prop == other.prop
        )

    def delta_from(self, older: "PropValue[X]", /) -> Any:
        match self.prop.diff_mode:
            case "eq":
                return self._value if self._value == older._value else SAME
            case "full":
                return self.prop.wrap(diff(self._value, older._value))
            case "never":
                return self._value

    def compute(self, key: str) -> tuple[str, X]:
        if self._cached:
            return self._cached
        self._cached = self.prop.transform(key, self._value)
        return self._cached

    def __pos__(self) -> X:
        return self.compute("")[1]
