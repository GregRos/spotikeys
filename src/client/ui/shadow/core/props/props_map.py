from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, Literal, overload
from pyrsistent import PMap, PRecord, m, pmap


from collections.abc import Mapping


@dataclass(frozen=True)
class ApplyInfo:
    converter: Callable[[Any], Any] | None
    value: Any
    name: str

    def compute(self):
        return self.converter(self.value) if self.converter else self.value


type Diff = Literal["recursive", "unit", "none"]

type DiffMap = dict[str, Diff]


class PropsMap:
    _diffs: DiffMap = dict()

    def __init__(self, diffs: DiffMap, props: PMap[str, PMap[str, ApplyInfo]] = m()):
        self._map = props or m()
        self._diffs = diffs

    def __iter__(self):
        return iter(self._map.items())

    def __getattr__(self, key: str) -> PMap[str, ApplyInfo]:
        return self._map[key]

    @overload
    def compute(self, group: str, key: str, /) -> Any: ...
    @overload
    def compute(self, group: str, /) -> PMap[str, Any]: ...

    @overload
    def compute(self, /) -> PMap[str, PMap[str, Any]]: ...

    def compute(self, group: str | None = None, key: str | None = None, /):
        if key:
            assert group, "Group must be provided when key is provided"
            return self._map[group][key].compute()

        def compute_group(group: str):
            return pmap(
                {value.name: value.compute() for key, value in self._map[group].items()}
            )

        if group:
            return compute_group(group)

        return pmap({group: compute_group(group) for group in self._map})

    @overload
    def get(self, key: str, /) -> PMap[str, ApplyInfo]: ...
    @overload
    def get(self, key: tuple[str, str], /) -> ApplyInfo: ...
    def get(self, key: str | tuple[str, str], /):
        if isinstance(key, tuple):
            group, key = key
            return self._map[group].get(key, m())
        return self._map.get(key, m())

    @overload
    def __getitem__(self, key: str, /) -> PMap[str, ApplyInfo]: ...

    @overload
    def __getitem__(self, key: tuple[str, str], /) -> ApplyInfo: ...

    def __getitem__(self, group: str | tuple[str, str], /):
        if isinstance(group, tuple):
            group, name = group
            return self._map[group].get(name, m())
        return self._map[group]

    def __contains__(self, key: str | tuple[str, str]) -> bool:
        if isinstance(key, tuple):
            group, key = key
            return group in self._map and key in self._map[group]
        return key in self._map

    def get_diff_type(self, group: str) -> Diff:
        return self._diffs.get(group, "none")

    @overload
    def set(self, group: str, value: PMap[str, ApplyInfo], /) -> "PropsMap": ...

    @overload
    def set(self, key: tuple[str, str], value: ApplyInfo, /) -> "PropsMap": ...

    def set(
        self, key: str | tuple[str, str], value: ApplyInfo | PMap[str, ApplyInfo], /
    ) -> "PropsMap":
        if isinstance(key, tuple):
            group, key = key
            assert isinstance(value, ApplyInfo)
            return PropsMap(
                self._diffs,
                self._map.set(group, self._map.get(group, m()).set(key, value)),
            )
        assert isinstance(value, Mapping)
        return PropsMap(self._diffs, self._map.set(key, value))

    def diff(self, other: "PropsMap") -> "PropsMap":
        result = PropsMap(self._diffs)
        for group_name, group in other:
            result = result.set(group_name, m())
            diff_type = self.get_diff_type(group_name)
            if group_name not in self or diff_type == "none":
                result = result.set(group_name, group)
            elif diff_type == "unit" and group != self[group_name]:
                result = result.set(group_name, group)
            elif diff_type == "recursive":
                for key, value in group.items():
                    key_pair = (group_name, key)
                    if key_pair not in self or self[key_pair] != value:
                        result = result.set(key_pair, value)

        return result
