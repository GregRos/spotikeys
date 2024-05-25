from dataclasses import dataclass, field


from copy import copy
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Literal,
    Self,
    Type,
    cast,
    get_type_hints,
    override,
)

from src.annotations.get_annotation_name import (
    get_annotation_name,
)
from src.annotations.get_metadata import get_inner_type_value, get_metadata_of_type


DiffMode = Literal["simple", "recursive", "never"]
if TYPE_CHECKING:
    from src.ui.model.prop_value import PropValue


@dataclass(kw_only=True)
class Prop:
    parent: str | None = field(default=None)
    alias: str | None = field(default=None)
    default: Any | None = field(default=None)
    converter: Callable[[Any], Any] | None = field(default=None)
    value_type: type[Any] | None = field(default=None)
    prop_name: str | None = field(default=None)

    @property
    def prop(self) -> "Prop":
        return self

    @property
    def has_default(self) -> bool:
        return self.default is not None

    @property
    def is_dict(self) -> bool:
        from src.ui.model.prop_dict import PropDict

        return self.value_type is PropDict

    def is_valid(self, input: Any):
        if self.value_type:
            if self.value_type is float:
                return isinstance(input, int) or isinstance(input, float)
            if get_annotation_name(self.value_type) == "Literal":
                return True
            return isinstance(input, self.value_type)
        return True

    def assert_valid_value(self, value: Any):
        if not self.is_valid(value):
            raise ValueError(f"Invalid value {value} for {self}")

    @property
    def value(self) -> Any:
        if self.default is None:
            raise ValueError("No default value set")
        return self.default

    def set(self, **kwargs: Any) -> "Prop":
        clone = copy(self)
        for k, v in kwargs.items():
            setattr(clone, k, v)
        return clone

    def transform(self, key: str, value: Any) -> tuple[str, Any]:
        return (self.alias or key, self.converter(value) if self.converter else value)

    def merge(self, other: "Prop") -> "Prop":
        return self.set(**{k: v for k, v in other.__dict__.items() if v is not None})

    def compute(self, key: str) -> tuple[str, Any] | None:
        return self.alias if self.alias else key, self.default


def get_props(section_type: Type):
    type_metadata = get_type_hints(section_type, include_extras=True)
    for k, v in type_metadata.items():
        inner_type = get_inner_type_value(v) or v
        prop_def = get_metadata_of_type(v, Prop)
        if not prop_def:
            prop_def = Prop(prop_name=k)
        yield k, prop_def.set(value_type=inner_type, prop_name=k)
