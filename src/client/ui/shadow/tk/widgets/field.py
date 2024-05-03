from dataclasses import _MISSING_TYPE, MISSING, dataclass, field
from tkinter import Widget
from typing import Any, Callable, Literal

from pyrsistent import PVector, v

from src.client.ui.shadow.core.props.field_apply_info import FieldApplyInfo

tage = Literal["configure", "place", "other"]


def prop[
    X
](
    subtype: str,
    /,
    *,
    default: X | _MISSING_TYPE = MISSING,
    converter: Callable[[X], Any] | None = None,
) -> X:
    if default is MISSING:
        return field(
            metadata={"apply": FieldApplyInfo(type=subtype, converter=converter)}
        )
    else:
        return field(
            default=default,
            metadata={"apply": FieldApplyInfo(type=subtype, converter=converter)},
        )


def configure_field[X](default: X, converter: Callable[[X], Any] | None = None) -> X:
    return field(
        default=default,
        metadata={"apply": FieldApplyInfo(type="configure", converter=converter)},
    )


def pack_field[X](default: X, converter: Callable[[X], Any] | None = None) -> X:
    return field(
        default=default, metadata={"apply": FieldApplyInfo("place", converter)}
    )


def other_field[X](default: X) -> X:
    return field(
        default=default,
        metadata={"apply": FieldApplyInfo("other")},
    )
