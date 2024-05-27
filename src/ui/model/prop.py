from dataclasses import dataclass, field
from typeguard import check_type
from copy import copy
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Concatenate,
    Literal,
    Self,
    Type,
    cast,
    get_args,
    get_origin,
    get_type_hints,
    overload,
    override,
)

from src.annotations.defaults import defaults, update
from src.annotations.get_annotation_name import (
    get_annotation_name,
)
from src.annotations.get_metadata import (
    get_inner_type_value,
    get_metadata_of_type,
    get_props_type_from_callable,
)
from src.ui.model.annotation_reader import AnnotationReader


DiffMode = Literal["simple", "recursive", "never"]
if TYPE_CHECKING:
    from src.ui.model.prop_value import PValue


@dataclass(kw_only=True)
class Prop:
    subsection: str | None = field(default=None)
    # FIXME: name behaves weirdly because it's inconsistent... should be fixed
    name: str | None = field(default=None)
    no_value: Any | None = field(default=None)
    converter: Callable[[Any], Any] | None = field(default=None)
    value_type: type[Any] | None = field(default=None)
    repr: Literal["simple", "recursive", "none"] = field(default="recursive")

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
            return check_type(input, self.value_type)
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

    def transform(self, key: str, value: Any) -> tuple[str, Any]:
        return (self.name or key, self.converter(value) if self.converter else value)

    def merge(self, other: "Prop") -> "Prop":
        return self.update(**{k: v for k, v in other.__dict__.items() if v is not None})

    def compute(self, key: str) -> tuple[str, Any] | None:
        return self.name if self.name else key, self.no_value

    def defaults(self, source_prop: "Prop") -> "Prop":
        return defaults(
            self, source_prop, "parent", "name", "no_value", "converter", "value_type"
        )

    def merge_setter(self, prop_setter: Callable) -> "Prop":
        prop_type = get_props_type_from_callable(prop_setter)
        prop_meta = self.defaults(Prop(value_type=prop_type, name=prop_setter.__name__))
        return prop_meta

    @overload
    def __call__[
        **P, R
    ](self, f: Callable[Concatenate[R, P], Any]) -> Callable[Concatenate[R, P], R]: ...

    @overload
    def __call__[
        **P, R
    ](self) -> Callable[
        [Callable[Concatenate[R, P], Any]], Callable[Concatenate[R, P], R]
    ]: ...

    def __call__[**P, R](self, f: Any | None = None) -> Any:
        def get_or_init_prop_values(self):
            if not getattr(self, "_props", None):
                self._props = AnnotationReader(self.__class__).section.with_values({})
            return self._props

        def apply(f):
            merged_prop = self.merge_setter(f)

            def set_prop(self, arg: Any):
                return self._copy(**{merged_prop.name: arg})

            AnnotationReader(set_prop).prop = merged_prop

            return set_prop

        return apply(f) if f else apply
