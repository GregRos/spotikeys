from __future__ import annotations
from functools import total_ordering
from typing import overload
from src.client.kb.key import Key


@total_ordering
class KeyCombination:
    __match_args__ = ("keys",)

    def __init__(self, keys: set[Key]):
        self.keys = frozenset(keys)

    def __iter__(self):
        return iter(self.keys)

    @property
    def is_empty(self):
        return not self.keys

    def is_pressed(self):
        return all(key.is_pressed() for key in self.keys)

    @property
    def specificity(self):
        return sum(key.specificity for key in self.keys)

    def __add__(self, other: Key | KeyCombination) -> KeyCombination:
        match other:
            case Key():
                return KeyCombination({*self.keys, other})
            case KeyCombination():
                return KeyCombination({*self.keys, *other.keys})

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, KeyCombination):
            return False
        return self.keys == value.keys

    def __hash__(self) -> int:
        return hash(self.keys)

    def __lt__(self, other: KeyCombination) -> bool:
        return (
            self.specificity < other.specificity
            if self.specificity != other.specificity
            else self.keys < other.keys
        )

    def __str__(self):
        if not self.keys:
            return "∅"
        return " ✕ ".join(str(key) for key in sorted(self.keys))
