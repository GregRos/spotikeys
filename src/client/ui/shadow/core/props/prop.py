from dataclasses import _MISSING_TYPE, MISSING, field
from typing import Any, Callable, Literal

from src.client.ui.shadow.core.props.field_apply_info import FieldApplyInfo


def prop[
    X
](
    subtype: str,
    /,
    *,
    default: X | _MISSING_TYPE = MISSING,
    converter: Callable[[X], Any] | None = None,
    diff=True,
) -> X:
    if default is MISSING:
        return field(
            metadata={
                "apply": FieldApplyInfo(type=subtype, converter=converter, diff=diff)
            }
        )
    else:
        return field(
            default=default,
            metadata={
                "apply": FieldApplyInfo(type=subtype, converter=converter, diff=diff)
            },
        )
