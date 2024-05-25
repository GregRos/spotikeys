from copy import copy
import functools
from inspect import isfunction
from itertools import groupby, starmap
import itertools
from typing import (
    TYPE_CHECKING,
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
    overload,
)

if TYPE_CHECKING:
    from src.client.ui.shadow.model.props.dict.props_dict import PropsDict, section
from src.client.ui.shadow.model.props.from_type.get_inner_type_value import (
    get_inner_type_value,
)
from src.client.ui.shadow.model.props.from_type.get_metadata import get_metadata
from src.client.ui.shadow.model.props.from_type.get_type_annotation import (
    AnnotationReader,
)
from src.client.ui.shadow.model.props.single.prop_def import PropDef


UNSET = object()


def get_props_type_from_callable(f: Callable):
    arg = next(
        x or v
        for k, v in get_type_hints(f, include_extras=True).items()
        if (x := get_inner_type_value(v))
    )
    return arg


def get_prop_def(t: Type):
    metadata = get_metadata(t)
    return next((x for x in metadata if isinstance(x, PropDef)), None)


def get_section_meta(f: Callable) -> "section | None":
    return f.__annotations__["section"]


def get_props(section_type: Type):
    type_metadata = get_type_hints(section_type, include_extras=True)
    for k, v in type_metadata.items():
        inner_type = get_inner_type_value(v) or v
        prop_def = get_prop_def(v)
        if not prop_def:
            continue
        yield k, prop_def.set(value_type=inner_type)
