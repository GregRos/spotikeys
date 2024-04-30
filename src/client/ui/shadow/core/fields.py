from dataclasses import dataclass, field
from typing import Any, Callable

from src.client.ui.shadow.core.property_dict import ApplyInfo
from src.client.ui.shadow.core.property_dict import ApplyKey
from src.client.ui.shadow.types import Stage


@dataclass(frozen=True)
class FieldApplyInfo[X]:
    stage: Stage = field(default="other")

    converter: Callable[[X], Any] | None = field(default=None)

    def to_apply_pair(
        self, prop_name: str, prop_value: X
    ) -> tuple[ApplyKey, ApplyInfo[X]]:
        return ApplyKey(self.stage, prop_name), ApplyInfo[X](prop_value, self.converter)


def configure_field[X](default: X, converter: Callable[[X], Any] | None = None) -> X:
    return field(
        default=default, metadata={"apply": FieldApplyInfo("configure", converter)}
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
