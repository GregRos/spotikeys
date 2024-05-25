from copy import copy
import functools
from inspect import isfunction
from itertools import groupby, starmap
import itertools
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    Concatenate,
    Mapping,
    NotRequired,
    Type,
    Unpack,
    cast,
    get_type_hints,
)

from src.client.ui.shadow.model.annotations.get_annotation_name import (
    get_prop_def,
    get_inner_type_value,
)


def get_props(section_type: Type):
    type_metadata = get_type_hints(section_type, include_extras=True)
    for k, v in type_metadata.items():
        inner_type = get_inner_type_value(v) or v
        prop_def = get_prop_def(v)
        if not prop_def:
            continue
        yield k, prop_def.set(value_type=inner_type, prop_name=k)
