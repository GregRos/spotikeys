from collections.abc import Mapping
from copy import copy
from dataclasses import dataclass, field
from inspect import isfunction
from itertools import groupby
from types import SimpleNamespace
from typing import (
    Any,
    Callable,
    Concatenate,
    Iterable,
    Iterator,
    Literal,
    NotRequired,
    Optional,
    Protocol,
    Self,
    TypedDict,
    Unpack,
    cast,
    get_type_hints,
    overload,
    override,
    runtime_checkable,
)

from pyrsistent import v


from src.annotations.get_metadata import get_props_type_from_callable
from src.annotations.get_methods import get_methods
from src.ui.model.annotation_reader import AnnotationReader
from src.ui.model.prop import Prop, get_props
from src.ui.model.prop_value import PropValue


from src.ui.tk.geometry import Geometry


type SomeProp = Prop | section
SAME = object()


class PropDict(Mapping[str, SomeProp]):
    _props: Mapping[str, SomeProp]

    def __init__(
        self, props: Mapping[str, SomeProp] | Iterable[tuple[str, SomeProp]] = {}
    ):
        self._props = (
            dict(props) if isinstance(props, Mapping) else {k: v for k, v in props}
        )

    def get_prop(self, key: str) -> Prop:
        result = self[key]
        assert isinstance(result, Prop), f"Key {key} is not a PropDef"
        return result

    def get_section(self, key: str) -> "section":
        result = self[key]
        assert isinstance(result, section), f"Key {key} is not a section"
        return result

    def __and__(self, other: Mapping[str, SomeProp]) -> "PropDict":
        return self.merge(other)

    def merge(
        self, other: Mapping[str, SomeProp] | Iterable[tuple[str, SomeProp]]
    ) -> "PropDict":
        result = {}
        other = PropDict(other)
        for key in self.keys() | other.keys():
            if key not in self:
                result[key] = other[key]
                continue
            elif key not in other:
                result[key] = self[key]
                continue
            self_prop = self[key]
            other_prop = other[key]
            assert isinstance(self_prop, section) and isinstance(
                other_prop, section
            ), f"Key {key} exists in both dicts, but is not a section in at least one. Can't be merged."
            result[key] = self_prop.merge_props(other_prop)

        return PropDict(result)

    def set(self, **props: Prop) -> "PropDict":
        return self.merge(props)

    def __len__(self) -> int:
        return len(self._props)

    def __iter__(self) -> Iterator[str]:
        return iter(self._props)

    def __getitem__(self, key: str) -> SomeProp:
        return self._props[key]

    def assert_match(self, other: Mapping[str, Any]) -> None:
        errors = []
        for key in self.keys() | other.keys():
            if key not in self:
                errors += [f"Key of input map {key} doesn't exist in self."]
            if key not in other:
                errors += [f"Key of self map {key} doesn't exist in input."]
            if self[key] != other[key]:
                errors += [f"Key {key} doesn't match."]

        if errors:
            raise ValueError("\n".join(errors))


@dataclass
class section(Mapping[str, SomeProp]):
    props: PropDict = field(default_factory=PropDict)
    recurse: bool = field(default=True)
    alias: str | None = field(default=None)
    name: str = field(default="", init=False)
    def __iter__(self) -> Iterator[str]:
        return iter(self.props)

    def with_values(self, values: Mapping[str, Any]) -> "PropVals":
        return PropVals(self, values)

    def __getitem__(self, key: str) -> SomeProp:
        return self.props[key]

    def __len__(self) -> int:
        return len(self.props)

    def transform(self, key: str, value: Any) -> tuple[str, Any]:
        assert isinstance(value, Mapping), f"Value {value} is not a mapping"
        return key, PropVals(self, value)

    def merge_props(self, other: "Mapping[str, SomeProp] | section") -> "section":
        merged_props = self.props & (
            other.props if isinstance(other, section) else other
        )
        clone = copy(self)
        clone.props = merged_props
        return clone

    __match_args__ = ("recurse",)

    def assert_valid_value(self, other: Mapping[str, Any]) -> None:
        assert isinstance(other, Mapping), f"Value {other} is not a mapping"
        for k, v in other.items():
            section = self.props
            value = section.get(k, None)
            if not value:
                raise ValueError(f"Key {k} doesn't exist in section {section}")
            value.assert_valid_value(v or value.default)  # type: ignore

    @overload
    def __call__[
        **P, R
    ](self, f: Callable[Concatenate[R, P], None]) -> Callable[Concatenate[R, P], R]: ...

    @overload
    def __call__[
        **P, R
    ](self) -> Callable[
        [Callable[Concatenate[R, P], Any]], Callable[Concatenate[R, P], R]
    ]: ...

    def __call__[**P, R](self, f: Any | None = None) -> Any:
        def get_or_init_prop_values(self):
            if not getattr(self, "_props", None):
                self._props = AnnotationReader(self.__class__).props.with_values({})
            return self._props

        def apply(f):
            sect = get_section(f, self)

            def set_section(self, **args: Any):
                if f.__name__ == "__init__":
                    self._props = get_or_init_prop_values(self).merge(args)
                    return
                return self._copy(**{f.__name__: args})

            AnnotationReader(set_section).section = sect

            return set_section

        return apply(f) if f else apply


class PropVals(Mapping[str, "PropValue | PropVals"]):
    section: "section"
    _vals: Mapping[str, Any]

    def __repr__(self) -> str:
        entries = dict()
        for key, value in self.items():
            prop = self.section.props[key]
            if isinstance(prop, section):
                entries[key] = f"{prop.}"
            entries[key] = value.value.__repr__()
        props = ", ".join("=".join(pair) for pair in entries.items())
        return props

    def without(self, *keys: str) -> "PropVals":
        return PropVals(self.section, {k: v for k, v in self.items() if k not in keys})

    def __getitem__(self, key: str) -> "PropValue | PropVals":
        value = self._vals.get(key)
        prop = self.section.props[key]
        if not value:
            if isinstance(prop, section):
                raise KeyError(f"Key {key} is a section, but doesn't exist in values")
            if prop.has_default:
                return PropValue(prop, prop.value)
            raise KeyError(f"Key {key} doesn't exist in values")
        if isinstance(prop, section):
            return PropVals(prop, value)
        return PropValue(prop, value)

    @property
    def value(self) -> Mapping[str, Any]:
        return self._vals

    def __init__(self, props: "section", values: Mapping[str, Any] = {}):
        self.section = props
        self._vals = {k: v for k, v in values.items() if v is not None}
        props.assert_valid_value(values)

    def __len__(self) -> int:
        return len(self._vals)

    def __iter__(self) -> Iterator[str]:
        return iter(self._vals)

    def merge(self, other: Mapping[str, Any]) -> "PropVals":
        return PropVals(self.section, dict(self._vals) | dict(other))

    @staticmethod
    def _diff(a: Any, b: Any) -> Any:
        if isinstance(a, PropVals):
            if not isinstance(b, PropVals):
                raise ValueError("Cannot diff PropVals with non-PropVals")
            return a.diff(b)
        if isinstance(b, PropVals):
            raise ValueError("Cannot diff PropVals with non-PropVals")
        if a == b:
            return SAME
        return b

    def diff(self, other: "PropVals") -> "PropVals":
        self.section.assert_valid_value(other._vals)
        out = {}
        for k, v in self.items():
            match v:
                case PropValue():
                    if v != other[k]:
                        out[k] = v.value
                case PropVals():
                    if v.section.recurse:
                        result = PropVals._diff(v, other._vals[k])
                        if result is not SAME:
                            out[k] = result.value
                    else:
                        if v != other._vals[k]:
                            out[k] = v.value

        return PropVals(self.section, out)

    def compute(self, key: str) -> tuple[str, dict[str, Any]]:
        result = {}
        name = self.section.alias or key

        def get_or_create_section(section: str):
            if section not in result:
                result[section] = {}
            return result[section]

        for key, prop_val in self.items():
            k, v = prop_val.compute(key)
            target = (
                get_or_create_section(prop_val.prop.parent)
                if isinstance(prop_val, PropValue) and prop_val.prop.parent
                else result
            )
            target[k] = v
        return name, result


def get_section(section_setter: Callable, section_meta: section) -> "section":
    section_props_type = get_props_type_from_callable(section_setter)
    props = PropDict()
    all_props = get_props(section_props_type)
    for k, v in all_props:
        props = props.merge({k: v})

    return section_meta.merge_props(props)


def get_section_meta(f: Callable) -> "section | None":
    return f.__annotations__["section"]


def get_sections(obj: type):
    props = PropDict()
    methods = get_methods(obj, stop_class=object)
    for k, f in methods.items():
        if not isfunction(f) or "section" not in AnnotationReader(f):
            continue
        section = AnnotationReader(f).section

        if k == "__init__":
            props = props.merge(section.props)
        else:
            props = props.merge({k: section})
    return props
