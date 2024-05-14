from copy import copy
from typing import (
    Annotated,
    Any,
    Callable,
    Concatenate,
    NotRequired,
    Type,
    Unpack,
    get_type_hints,
)

from src.client.ui.shadow.core.props.dict.props_dict import PropsDict
from src.client.ui.shadow.core.props.single.prop_def import PropDef

UNSET = object()


def get_origin(t: Type, default=UNSET):
    if default is UNSET:
        return getattr(t, "__origin__")
    else:
        return getattr(t, "__origin__", default)


def get_inner_type_value(t: Type):
    origin = get_origin(t, None)
    if origin is Unpack or origin is NotRequired or origin is Annotated:
        return t.__args__[0]  # type: Type
    else:
        return None


def get_metadata(t: Type):
    origin = get_origin(t, None)
    if origin is Annotated:
        return t.__metadata__  # type: tuple[Type, ...]
    else:
        return ()  # type: tuple[Type, ...]


def get_section_type(f: Callable):
    arg = next(
        x or v for k, v in get_type_hints(f).items() if (x := get_inner_type_value(v))
    )
    return arg


def get_props(obj: Callable):
    section_type = get_section_type(obj)
    for k, v in section_type.items():
        inner_type = get_inner_type_value(v) or v
        annotations = get_metadata(v)
        if annotations:
            prop_def = annotations[0]
            yield k, prop_def.set(value_type=inner_type)
        else:
            yield k, PropDef(value_type=inner_type)


def make_props_from_annotated(obj: Callable):
    return PropsDict({k: v for k, v in get_props(obj)})


def section_setter[
    **P, R, X
](prop_def: PropDef = PropDef(value_type=PropsDict)) -> Callable[
    [Callable[Concatenate[R, P], Any]], Callable[Concatenate[R, P], R]
]:
    def init_props_dict(target: Any):
        if not hasattr(target, "_props"):
            result = PropsDict({})
            setattr(target, "_props", result)
        target = getattr(target, "_props")
        return target  # typ

    def decorator(
        f: Callable[Concatenate[R, P], None]
    ) -> Callable[Concatenate[R, P], R]:

        def setter(self: R, *args: P.args, **kwargs: P.kwargs) -> R:
            if f.__name__ == "__init__":
                name = "default"
                target = self
            else:
                name = f.__name__
                target = copy(self)

            target = init_props_dict(target)
            props = make_props_from_annotated(f)
            props = props.merge(kwargs)
            target[name] = props
            return target

        return setter

    return decorator
