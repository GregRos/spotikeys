from copy import copy
from itertools import groupby
from typing import Callable, Concatenate

from src.client.ui.shadow.model.props.dict.props_dict import PropsDict
from src.client.ui.shadow.model.props.from_type.read_annotations import (
    get_sections,
)


def section_setter[
    **P, R
](self, f: Callable[Concatenate[R, P], None]) -> Callable[Concatenate[R, P], R]: ...


def section_setter[
    **P, R
](self) -> Callable[
    [Callable[Concatenate[R, P], Any]], Callable[Concatenate[R, P], R]
]: ...


def section_setter[**P, R](self, f: Any | None = None) -> Any:
    def get_init_props(target: Any):
        return getattr(target, "_props", PropsDict({}))

    def decorator(
        f: Callable[Concatenate[R, P], None]
    ) -> Callable[Concatenate[R, P], R]:

        def setter(self: R, *args: P.args, **kwargs: P.kwargs) -> R:
            if f.__name__ == "__init__":
                name = None
                target = self
            else:
                name = f.__name__
                target = copy(self)
            root_props = PropsDict()
            these_props = get_sections(f)
            by_section = groupby(these_props lambda x: x[1].section)
            for section, props in by_section:
                section_props = PropsDict({key: prop for key, prop in props})
                if section_props:
                    root_props = root_props.merge({section: section_props})

            these_props = these_props.with_values(kwargs)
            if "key" in these_props:
                root_props = root_props.set(key=these_props["key"])
            setattr(target, "_props", root_props)
            return root_props if f.__name__ != "__init__" else None  # type: ignore

        return setter

    return decorator(f) if f else decorator
