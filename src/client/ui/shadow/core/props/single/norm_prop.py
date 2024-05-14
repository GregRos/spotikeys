from typing import Literal, overload

from src.client.ui.shadow.core.props.single.just_value import JustValue
from src.client.ui.shadow.core.props.single.prop_def import PropDef
from src.client.ui.shadow.core.props.single.prop_value import PropValue


type SomeProp[X] = PropValue[X] | PropDef[X] | JustValue[X]


@overload
def norm_prop[X](a: PropDef[X] | None, b: PropDef[X], /) -> PropDef[X]: ...
@overload
def norm_prop[X](a: PropValue[X], b: PropDef[X], /) -> PropValue[X]: ...
@overload
def norm_prop[X](a: PropDef[X], b: PropValue[X], /) -> PropValue[X]: ...
@overload
def norm_prop[
    X
](maybe_a: SomeProp[X] | None, maybe_b: SomeProp[X] | None, /) -> SomeProp[X]: ...
def norm_prop[
    X
](maybe_a: SomeProp[X] | None, maybe_b: SomeProp[X] | None, /) -> SomeProp[X]:
    match maybe_a, maybe_b:
        case None, None:
            assert False, "Expected a value"
        case None, prop if prop is not None:
            return prop
        case prop, None if prop is not None:
            return prop
        case (PropDef() as prop) | PropValue(_, prop), PropValue() as oth:
            return prop.merge(oth.prop).wrap(oth.value)
        case JustValue(), JustValue() as oth:
            return oth
        case JustValue(value), PropDef() as prop:
            return PropValue(value, prop)
        case (PropDef() as prop) | PropValue(_, prop), JustValue(value):
            return PropValue(value=value, prop=prop)
        case _:
            assert False, f"Unexpected combination {maybe_a} and {maybe_b}"
