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

from src.annotations.defaults import defaults, update
from src.annotations.get_annotation_name import (
    get_annotation_name,
)
from src.annotations.get_metadata import get_inner_type_value, get_metadata_of_type


DiffMode = Literal["simple", "recursive", "never"]
if TYPE_CHECKING:
    from src.ui.model.prop_value import PValue


@dataclass(kw_only=True)
class Prop:
    subsection: str | None = field(default=None)
    name: str | None = field(default=None)
    no_value: Any | None = field(default=None)
    converter: Callable[[Any], Any] | None = field(default=None)
    value_type: type[Any] | None = field(default=None)

    @property
    def prop(self) -> "Prop":
        return self

    @property
    def has_default(self) -> bool:
        return self.no_value is not None

    @property
    def is_dict(self) -> bool:
        from src.ui.model.prop_dict import PDict

        return self.value_type is PDict

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
        if self.no_value is None:
            raise ValueError("No default value set")
        return self.no_value

    def update(self, source_prop: "Prop") -> "Prop":
        return update(
            self, source_prop, "parent", "name", "no_value", "converter", "value_type"
        )

    def defaults(self, source_prop: "Prop") -> "Prop":
        return defaults(
            self, source_prop, "parent", "name", "no_value", "converter", "value_type"
        )

    def transform(self, key: str, value: Any) -> tuple[str, Any]:
        return (self.name or key, self.converter(value) if self.converter else value)

    def merge(self, other: "Prop") -> "Prop":
        return self.update(**{k: v for k, v in other.__dict__.items() if v is not None})

    def compute(self, key: str) -> tuple[str, Any] | None:
        return self.name if self.name else key, self.no_value
