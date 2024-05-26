from dataclasses import dataclass
from typing import Any
from pydantic import ConfigDict

from src.ui.model.prop_dict import PValues
from src.ui.model.shadow_node import ShadowNode
from src.ui.model.resource import ShadowedResource


@dataclass
class Create:
    next: ShadowNode

    def __repr__(self) -> str:
        return f"🆕 {self.next}"


@dataclass
class Update:
    existing: ShadowedResource
    next: ShadowNode
    diff: PValues

    def __bool__(self):
        return bool(self.diff.value)

    @property
    def props(self):
        return self.existing.props(self.next._props)

    def __repr__(self) -> str:
        return f"📝 {self.diff}"


@dataclass
class Recreate:
    old: ShadowedResource
    next: ShadowNode

    @property
    def props(self):
        return f"{self.old.key} ♻️ {self.next._props}"


@dataclass
class Place:
    what: Update | Recreate | Create

    def __repr__(self) -> str:
        return f"👇 {self.what.__repr__()}"


@dataclass
class Replace:
    replaces: ShadowedResource
    with_what: Update | Recreate | Create

    def __repr__(self) -> str:
        return f"{self.replaces.key} ↔️ {self.with_what.__repr__()}"


@dataclass
class Unplace:
    what: ShadowedResource

    def __repr__(self) -> str:
        return f"❌ {self.what.key}"
