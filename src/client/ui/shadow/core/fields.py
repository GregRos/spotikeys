from dataclasses import dataclass, field
from tkinter import Widget
from typing import Any, Callable, Literal

from pyrsistent import PVector, v

from src.client.ui.shadow.core.reconciler.property_dict import ApplyInfo
from src.client.ui.shadow.core.reconciler.property_dict import ApplyKey

tage = Literal["configure", "place", "other"]


@dataclass(frozen=True)
class FieldApplyInfo[X]:
    type: str
    converter: Callable[[X], Any] | None = field(default=None)


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
