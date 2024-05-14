from src.client.ui.shadow.model.props.single.prop_def import PropDef
from src.client.ui.shadow.model.props.operators import SAME, Computable, Diffable, diff
from src.client.ui.shadow.model.props.single.just_value import JustValue


from pydantic import Field
from pydantic.dataclasses import dataclass


from typing import Any


@dataclass(kw_only=True)
class PropValue[X](Computable, Diffable):
    __match_args__ = ("value", "prop")
    __slots__ = ("_cached", "value")
    _cached: tuple[str, X] | None = Field(default=None)

    def __init__(self, value: X, prop: PropDef[X]):
        self.value = value
        self.prop = prop
        self._cached = None

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, PropValue)
            and self.value == other.value
            and self.prop == other.prop
        )

    def delta_from(self, older: "PropValue[X]", /) -> Any:
        match self.prop.diff_mode:
            case "eq":
                return self.value if self.value == older.value else SAME
            case "full":
                return self.prop.wrap(diff(self.value, older.value))
            case "never":
                return self.value

    def compute(self, key: str) -> tuple[str, X]:
        if self._cached:
            return self._cached
        self._cached = self.prop.transform(key, self.value)
        return self._cached

    def __pos__(self) -> X:
        return self.compute("")[1]
