from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from src.ui.model.shadow_node import ShadowNode
from src.ui.model.resource import ShadowedResource


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Create:
    next: ShadowNode

    def __repr__(self) -> str:
        return f"🆕 {self.next}"


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Update:
    existing: ShadowedResource
    next: ShadowNode

    @property
    def props(self):
        return self.existing.props(self.next._props)

    def __repr__(self) -> str:
        return f"📝 {self.next._props}"


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Recreate:
    old: ShadowedResource
    next: ShadowNode

    @property
    def props(self):
        return f"{self.old.key} ♻️ {self.next._props}"


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Place:
    what: Update | Recreate | Create

    def __repr__(self) -> str:
        return f"👇 {self.what.__repr__()}"


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Replace:
    replaces: ShadowedResource
    with_what: Update | Recreate | Create

    def __repr__(self) -> str:
        return f"{self.replaces.key} ↔️ {self.with_what.__repr__()}"


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Unplace:
    what: ShadowedResource

    def __repr__(self) -> str:
        return f"❌ {self.what.key}"
