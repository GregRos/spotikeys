from copy import copy
from typing import Any


def is_empty(target, key) -> bool:
    x = getattr(target, key)
    return x is None or x == "" or x == []


def defaults[T](self, base: T, *only_keys: str) -> T:
    clone = copy(self)
    for k, v in base.__dict__.items():
        if only_keys and k not in only_keys:
            continue
        if is_empty(clone, k) and v is not None:
            setattr(clone, k, v)
    return clone


def update[T](self, base: T, *only_keys: str) -> T:
    clone = copy(self)
    for k, v in base.__dict__.items():
        if only_keys and k not in only_keys:
            continue
        if v is not None:
            setattr(clone, k, v)
    return clone
