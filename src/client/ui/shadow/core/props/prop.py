from dataclasses import _MISSING_TYPE, MISSING, field
from typing import Any, Callable, Literal

from src.client.ui.shadow.core.props.prop_info import PropInfo


def prop[
    X
](
    subtype: str,
    /,
    *,
    name: str | None = None,
    default: X | _MISSING_TYPE = MISSING,
    converter: Callable[[X], Any] | None = None,
) -> X:
    metadata_object = {"prop": PropInfo(type=subtype, name=name, converter=converter)}
    if default is MISSING:
        return field(metadata=metadata_object)
    else:
        return field(
            default=default,
            metadata=metadata_object,
        )
