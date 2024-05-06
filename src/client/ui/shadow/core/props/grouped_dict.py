from abc import abstractmethod
from dataclasses import MISSING, dataclass, field
from numbers import Number
from typing import Any, Callable, Iterator, Literal, Protocol, Self, TypeGuard,  overload, override, runtime_checkable


from collections.abc import Mapping

from pydantic import validate_call
from pydantic_core import Some

@runtime_checkable
class Diffable[DiffType](Protocol):
    @abstractmethod
    def diff_to(self, other: object, /) -> DiffType: ...

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Diffable) and self.diff_to(other) == SAME
    
@runtime_checkable    
class Computable[Value](Protocol):
    @abstractmethod
    def compute(self) -> Value: ...
    
    @abstractmethod
    def __eq__(self, other: object) -> bool: ...
        
def compute(value: object, /) -> object:
    def compute_dict(value: Mapping[str, Any], /) -> dict[str, Any]:
        result = {}
        for key, val in value.items():
            result[key] = compute(val)
        return result
    if isinstance(value, Computable):
        return value.compute()
    if isinstance(value, Mapping):
        return compute_dict(value)
    return value

def diff(left: object, right: object, /) -> object:
    def diff_dicts(left: Mapping[str, Any], right: Mapping[str, Any], /) -> Mapping[str, Any]:
        result = {}
        for key in left.keys() | right.keys():
            if key not in right:
                result[key] = REMOVED
                continue
            if key not in left:
                result[key] = right[key]
                continue
            l_val, r_val = left[key], right[key]
            difference = diff(l_val, r_val)
            if difference is not SAME:
                result[key] = difference
        return result
    if isinstance(left, Diffable) and isinstance(right, Diffable):
        return left.diff_to(right)

    if isinstance(right, Mapping) and isinstance(left, Mapping):
        return diff_dicts(left, right) or SAME
    
    if right == left:
        return SAME
    return right


class GroupedDict[V]:
    def __init__(self):
        self._map = dict[str, V]()

    def __getattr__(self, key: str) -> dict[str, V]:
        return self[key]

    @overload
    def __getitem__(self, group: str, /) -> dict[str, V]: ...

    @overload
    def __getitem__(self, group: tuple[str, str], /) -> V | None: ...
    
    @validate_call()
    def __getitem__(self, arg: str | tuple[str, str], /) -> V | dict[str, V] | None:
        match arg:
            case str(group):
                return self._map.get(group, {})
            case (group, key):
                return self._map.get(group, {}).get(key, None)
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



class DiffResult:
    def __init__(self, name: str, truthy: bool):
        self.name = name
        self.truthy = truthy
    
    def __bool__(self):
        return self.truthy
    
    def __eq__(self, other: Any):
        return isinstance(other, DiffResult) and self.name == other.name or self.name == other
    
    def __str__(self):
        return f"!{self.name}!"

SAME = DiffResult("SAME", True)
REMOVED = DiffResult("REMOVED", False)
type DiffOp = Callable[[Any, Any], Any]
type InnerDict = Mapping[str, DiffOp | InnerDict]

class Diff:
    class Simple:
        def __call__(self, left: Any, right: Any):
            return right if left != right else SAME
    class OperatorDict(Mapping[str, DiffOp | "OperatorDict"]):
        def __init__(self, inner: InnerDict):
            result = {}
            for key, value in inner.items():
                if isinstance(value, Mapping):
                    result[key] = Diff.OperatorDict(value)
                else:
                    result[key] = value
            self._inner = result
            
        @override
        def __getitem__(self, key: str) -> Any:
            return self._inner.get(key, None) or self._inner.get("*", None) or Diff.Simple()
        
        def __call__(self, left: Any, right: Any) -> dict[str, Any]:
            result = {}
            for k in left.keys() | right.keys():
                if k not in right:
                    result[k] = REMOVED
                    continue
                if k not in left:
                    result[k] = right[k]
                    continue
                l_val, r_val = left[k], right[k]
                operator = self[k]
                compare = operator(l_val, r_val)
                assert compare != REMOVED, f"REMOVED is not a valid result here."
                if compare != SAME:
                    result[k] = compare
            return result

    
    class MapRecurse:
        def __init__(self, operators_dict: InnerDict):
            self._operators = operators_dict
            
        def _get_operator(self, key: str):
            return self._operators.get(key, None) or self._operators.get("*", None) or Diff.Simple()
            
        def _diff_from_left[V](self, left: Mapping[str, V], right: Mapping[str, V]):
            result = {}
            for k in left.keys() | right.keys():
                if k not in right:
                    result[k] = REMOVED
                    continue
                if k not in left:
                    result[k] = right[k]
                    continue
                l_val, r_val = left[k], right[k]
                operator = self._get_operator(k)
                compare = operator(l_val, r_val)
                assert compare != REMOVED, f"REMOVED is not a valid result here."
                if compare != SAME:
                    result[k] = compare
            return result
            
        def _recurse[V](self, left: Any, right: Any):
            match left, right:
                case Mapping(), Mapping():
                    return self._diff_maps(left, right)
                case (Mapping(), _):
                    raise ValueError(f"Right must be a Mapping, not {type(right)}")
                case (_, Mapping()):
                    raise ValueError(f"Left must be a Mapping, not {type(left)}")
                case _:
                    return right if left != right else SAME


class RecursiveDiffOperator:
    def __init__(self, depth=1):
        self.depth = depth
    
    def _recurse[V](self, depth: int, left: Mapping[str, V], right: Mapping[str, V]) -> Mapping[str, V]:
        result = {}
        assert isinstance(left, Mapping), f"Left must be a Mapping, not {type(left)}"
        assert isinstance(right, Mapping), f"Right must be a Mapping, not {type(right)}"
        if depth == 0:
            return right if left != right else {}
        for r_key, r_val in right.items():
            if r_key not in left:
                result[r_key] = r_val
                continue
            l_val = left[r_key]
            if isinstance(l_val, Mapping) and isinstance(r_val, Mapping):
                result[r_key] = self._recurse(depth - 1, l_val, r_val)
            elif l_val != r_val:
                result[r_key] = r_val
            

    def __call__[
        V
    ](self, left: Mapping[str, V], right: Mapping[str, V]) -> Mapping[str, V]:
        def _recurse(depth: int, left: Mapping[str, V], right: Mapping[str, V]):
        


class DiffOperator:
    def __init__(self, diff_policy: DiffPolicy):
        self._diff_policy = diff_policy

    def __call__(self, other: GroupedDict[V]) -> GroupedDict[V]:
        return other.diff(self._diff_policy)
