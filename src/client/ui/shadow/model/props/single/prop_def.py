from dataclasses import dataclass, field
from src.client.ui.shadow.model.props.operators import SAME, Computable, Diffable


from pydantic import Field


from copy import copy
from typing import TYPE_CHECKING, Any, Callable, Literal, Self, cast, override

DiffMode = Literal["simple", "recursive", "never"]
if TYPE_CHECKING:
    from src.client.ui.shadow.model.props.single.prop_value import PropValue


@dataclass(kw_only=True)
class PropDef(Computable, Diffable):
    section: str | None = field(default=None)
    alias: str | None = field(default=None)
    default: Any | None = field(default=None)
    converter: Callable[[Any], Any] | None = field(default=None)
    value_type: type[Any] | None = field(default=None)

    @property
    def prop(self) -> "PropDef":
        return self

    @property
    def has_default(self) -> bool:
        return self.default is not None

    @property
    def is_dict(self) -> bool:
        from src.client.ui.shadow.model.props.dict.props_dict import PropsDict

        return self.value_type is PropsDict

    def is_valid(self, input: Any):
        if self.value_type:
            return isinstance(input, self.value_type)
        return True

    @property
    def value(self) -> Any:
        if self.default is None:
            raise ValueError("No default value set")
        return self.default

    @override
    def delta_from(self, other: Self) -> Any:
        return self if self != other else SAME

    def set(self, **kwargs: Any) -> "PropDef":
        clone = copy(self)
        for k, v in kwargs.items():
            setattr(clone, k, v)
        return clone

    def transform(self, key: str, value: Any) -> tuple[str, Any]:
        return (self.alias or key, self.converter(value) if self.converter else value)

    def __bool__(self) -> bool:
        return False

    def merge(self, other: "PropDef") -> "PropDef":
        return self.set(**{k: v for k, v in other.__dict__.items() if v is not None})

    def compute(self, key: str) -> tuple[str, Any] | None:
        return self.alias if self.alias else key, self.default

