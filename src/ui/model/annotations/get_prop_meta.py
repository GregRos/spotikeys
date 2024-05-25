from typing import TYPE_CHECKING, Any, Callable, Type, get_type_hints
from src.ui.model.annotations.get_annotation_name import (
    get_annotation_name,
)
from src.ui.model.prop_def import PropDef

if TYPE_CHECKING:
    from src.ui.model.props_dict import section


def get_metadata(t: Type) -> tuple[Any, ...]:
    origin = get_annotation_name(t)
    if origin == "Annotated":
        return t.__metadata__  # type: tuple[Type, ...]
    else:
        return ()  # type: tuple[Type, ...]


def get_prop_def(t: Type):
    metadata = get_metadata(t)
    return next((x for x in metadata if isinstance(x, PropDef)), None)


def get_section_meta(f: Callable) -> "section | None":
    return f.__annotations__["section"]


def get_inner_type_value(ty: Type):
    t = ty
    while t is not None:
        annotation_name = get_annotation_name(t)
        if annotation_name in ("Annotated", "NotRequired", "Unpack"):
            t = t.__args__[0]  # type: Type
        else:
            return t


def get_props_type_from_callable(f: Callable):
    arg = next(
        x or v
        for k, v in get_type_hints(f, include_extras=True).items()
        if (x := get_inner_type_value(v))
    )
    return arg
