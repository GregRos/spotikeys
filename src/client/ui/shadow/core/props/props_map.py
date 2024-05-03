from dataclasses import dataclass
from typing import Any, Callable, Iterator


@dataclass(frozen=True)
class ApplyInfo:
    converter: Callable[[Any], Any] | None
    value: Any


from pyrsistent import PMap


from collections.abc import Mapping


class PropsMap(Mapping[str, ApplyInfo]):
    def __init__(self, props: PMap[str, ApplyInfo] = PMap()):
        self._map = props

    def __iter__(self) -> Iterator[str]:
        return iter(self._map)

    def compute(self):
        return {
            key: value.converter(value.value) if value.converter else value.value
            for key, value in self._map.items()
        }

    def __getitem__(self, key: str) -> ApplyInfo:
        return self._map[key]

    def set(self, key: str, value: ApplyInfo) -> "PropsMap":
        return PropsMap(self._map.transform(key, value))

    def diff(self, other: "PropsMap") -> "PropsMap":
        result = PMap[str, ApplyInfo]()
        for key, value in self._map.items():
            if key not in other._map or other[key] != value:
                result = result.transform(key, value)
        return PropsMap(result)
