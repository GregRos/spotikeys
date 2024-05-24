from copy import copy
import functools
from itertools import groupby, starmap
import itertools
from typing import (
    Annotated,
    Any,
    Callable,
    Concatenate,
    Mapping,
    NotRequired,
    Type,
    Unpack,
    cast,
    get_type_hints,
)

from src.client.ui.shadow.model.props.dict.props_dict import PropsSection, PropsDict
from src.client.ui.shadow.model.props.from_type.get_inner_type_value import (
    get_inner_type_value,
)
from src.client.ui.shadow.model.props.from_type.get_metadata import get_metadata
from src.client.ui.shadow.model.props.single.prop_def import PropDef


UNSET = object()


def get_props_type_from_callable(f: Callable):
    arg = next(
        x or v
        for k, v in get_type_hints(f, include_extras=True).items()
        if (x := get_inner_type_value(v))
    )
    return arg


def get_section(section_type: Type):
    type_metadata = get_type_hints(section_type, include_extras=True)
    for k, v in type_metadata.items():
        inner_type = get_inner_type_value(v) or v
        v_metadata = get_metadata(v)

        if prop_def := next((x for x in v_metadata if isinstance(x, PropDef)), None):
            yield k, prop_def.set(value_type=inner_type)
        elif prop_section := next(
            (x for x in v_metadata if isinstance(x, PropsSection)), None
        ):
            yield k, prop_section
        else:
            yield k, PropDef(value_type=inner_type)


def get_sections(obj: Type):
    props = PropsDict()
    hints = get_type_hints(obj, include_extras=True)
    for k, v in hints.items():
        if not callable(v):
            continue
        section_type = get_props_type_from_callable(v)
        section = get_section(section_type)
        if k == "__init__":
            props = props.merge(section)
    by_section = [*groupby(section, lambda x: x[1].section)]
    for section, section in by_section:
        if section is None:
            for key, prop in section:
                yield key, prop
        yield cast(str, section), PropsSection(PropsDict(section))


def get_props_dict_from_annotated(obj: Callable | Type):
    return PropsDict(get_sections(obj))


def section_setter[
    **P, R, X
](prop_def: PropDef = PropDef(value_type=PropsDict)) -> Callable[
    [Callable[Concatenate[R, P], Any]], Callable[Concatenate[R, P], R]
]:
    def props_from_annotations(target: Any, f: Callable) -> PropsDict:
        existing_props = getattr(target, "_props", None)
        if not existing_props:
            existing_props = PropsDict()
            setattr(target, "_props", existing_props)

        props = get_props_dict_from_annotated(f)
        return props

    def should_apply_props(target: Any, setter_name: str) -> PropsDict | None:
        init_props = getattr(target, "_init_props", set())
        if setter_name in init_props:
            return None

    def decorator(
        f: Callable[Concatenate[R, P], None]
    ) -> Callable[Concatenate[R, P], R]:

        def setter(self: R, *args: P.args, **kwargs: P.kwargs) -> R:
            if f.__name__ == "__init__":
                name = "default"
                target = self._props
            else:
                name = f.__name__
                target = copy(self)
            my_props = should_apply_props(self)
            props_from_type = get_props_dict_from_annotated(f)
            my_props = my_props.merge()
            props = [*get_props_dict_from_annotated(f)]
            target = should_apply_props(target)
            props = props.merge(kwargs)
            target[name] = props
            return target

        return setter

    return decorator
