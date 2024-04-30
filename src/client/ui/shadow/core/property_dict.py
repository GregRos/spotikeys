from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any, Callable

from attr import dataclass


from src.client.ui.shadow.types import Stage


@dataclass(frozen=True)
class ApplyInfo[X]:
    value: X
    converter: Callable[[X], Any] | None = field(default=None)


@dataclass(frozen=True)
class ApplyKey:
    stage: Stage
    prop_name: str


PropertyDict = dict[ApplyKey, ApplyInfo[Any]]


def compute_diff(prev_dict: PropertyDict, next_dict: PropertyDict) -> PropertyDict:
    previous_keys = set(prev_dict.keys())
    next_keys = set(next_dict.keys())
    all_keys = previous_keys.union(next_keys)
    result = {}
    for key in all_keys:
        prev = prev_dict.get(key)
        next = next_dict.get(key)
        if prev != next:
            result[key] = next_dict
    return result


def compute_values(d: PropertyDict) -> dict[Stage, dict[str, Any]]:
    stages: list[Stage] = ["configure", "place", "other"]
    return {
        stage: {
            key.prop_name: (
                apply_info.converter(apply_info.value)
                if apply_info.converter
                else apply_info.value
            )
            for key, apply_info in d.items()
            if key.stage == stage
        }
        for stage in stages
    }
