from dataclasses import dataclass, field
from typing import Any, Callable, Iterator, Literal, Self, overload, override


from collections.abc import Mapping


@dataclass(frozen=True)
class UncomputedValue:
    converter: Callable[[Any], Any] | None
    value: Any
    name: str

    def compute(self):
        return self.converter(self.value) if self.converter else self.value


type Diff = Literal["recursive", "unit", "none"]

type DiffPolicy = dict[str, Diff]


class GroupedDict[V](Mapping[str, dict[str, V]]):
    _diff_policy: DiffPolicy = dict()

    def __len__(self) -> int:
        return len(self._map)

    def __init__(self, diff_policy: DiffPolicy, props: dict[str, dict[str, V]] = {}):
        self._map = props or {}
        self._diff_policy = diff_policy

    def __iter__(self):
        return iter(self._map)

    def __getattr__(self, key: str) -> dict[str, V]:
        return self[key]

    @overload
    def __getitem__(self, group: str, /) -> dict[str, V]: ...

    @overload
    def __getitem__(self, group: str, key: str, /) -> V | None: ...

    @overload
    def __getitem__(self, group: tuple[str, str], /) -> V | None: ...

    def __getitem__(self, *args):
        match args:
            case (group, key),:
                assert isinstance(key, str), "Key must be string"
                assert isinstance(group, str), "Group must be string"
                return self._map.get(group, {}).get(key, None)
            case group,:
                assert isinstance(group, str), "Group must be string"
                return self._map.get(group, {})
            case _:
                raise ValueError("Invalid arguments")

    def __contains__(self, key: object) -> bool:
        if isinstance(key, tuple):
            group, key = key
            return group in self._map and key in self._map[group]
        return key in self._map

    def get_diff_type(self, group: str) -> Diff:
        return self._diff_policy.get(group, "none")

    @overload
    def __setitem__(self, key: str, value: dict[str, V], /): ...

    @overload
    def __setitem__(self, key: tuple[str, str], value: V, /): ...

    def __setitem__(self, *args: Any):
        match args:
            case (
                group,
                key,
            ), value:
                assert isinstance(key, str), "Key must be string"
                assert isinstance(group, str), "Group must be string"
                cur = self._map.get(group, {})
                self._map[group] = cur
                cur[key] = value
            case key, value:
                assert isinstance(key, str), "Key must be string"
                assert isinstance(value, dict), "Value must be dict"
                self._map[key] = value
            case _:
                raise ValueError("Invalid arguments")

    def to_dict(self) -> dict[str, dict[str, V]]:
        return self._map

    def transform[U](self, operator: Callable[[V], U]) -> "GroupedDict[U]":
        d = GroupedDict[U](self._diff_policy)
        for group, values in self._map.items():
            for key, value in values.items():
                d[group, key] = operator(value)
        return d

    def diff(self, other: "GroupedDict[V]") -> "GroupedDict[V]":
        result = GroupedDict(self._diff_policy)
        for group_name, group in other.items():
            diff_type = self.get_diff_type(group_name)
            if group_name not in self or diff_type == "none":
                result[group_name] = group
            elif diff_type == "unit" and group != self[group_name]:
                result[group_name] = group
            elif diff_type == "recursive":
                for key, value in group.items():
                    key_pair = (group_name, key)
                    if key_pair not in self or self[key_pair] != value:
                        result[key_pair] = value

        return result
