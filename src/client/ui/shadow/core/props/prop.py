from dataclasses import _MISSING_TYPE, MISSING, field
from typing import Any, Callable, Literal

from src.client.ui.shadow.core.props.field_apply_info import FieldApplyInfo


def prop[
    X
](
    subtype: str,
    /,
    *,
    name: str | None = None,
    default: X | _MISSING_TYPE = MISSING,
    converter: Callable[[X], Any] | None = None,
    diff=True,
) -> X:
    metadata_object = {
        "apply": FieldApplyInfo(type=subtype, name=name, converter=converter, diff=diff)
    }
    if default is MISSING:
        return field(metadata=metadata_object)
    else:
        return field(
            default=default,
            metadata=metadata_object,
        )
