from src.client.ui.shadow.model.props.single.prop_def import PropDef
from src.client.ui.shadow.model.props.dict.props_dict import PropsDict
from src.client.ui.shadow.model.props.dict.read_annotations import (
    make_props_from_annotated,
)


from pydantic.dataclasses import dataclass


from copy import copy
from typing import Any, Callable, Concatenate, overload


@dataclass(kw_only=True)
class PropSection(PropDef):

    @overload
    def section_setter[
        **P, R
    ](self, f: Callable[Concatenate[R, P], None]) -> Callable[Concatenate[R, P], R]: ...
    @overload
    def section_setter[
        **P, R
    ](self) -> Callable[
        [Callable[Concatenate[R, P], Any]], Callable[Concatenate[R, P], R]
    ]: ...
    def section_setter[**P, R](self, f: Any = None) -> Any:
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

        return decorator(f) if f else decorator
