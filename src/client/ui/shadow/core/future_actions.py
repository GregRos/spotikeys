from pydantic import ConfigDict
from pydantic.dataclasses import dataclass

from src.client.ui.shadow.model.props.operators import diff
from src.client.ui.shadow.model.nodes.shadow_node import ShadowNode
from src.client.ui.shadow.model.nodes.resource import ShadowedResource


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Create:
    next: ShadowNode


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Update:
    existing: ShadowedResource
    next: ShadowNode

    @property
    def props(self):
        return diff(self.existing.node._props, self.next._props)


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Recreate:
    old: ShadowedResource
    next: ShadowNode

    @property
    def props(self):
        return self.next._props


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Place:
    what: Update | Recreate | Create


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Replace:
    replaces: ShadowedResource
    with_what: Update | Recreate | Create


@dataclass(config=ConfigDict(arbitrary_types_allowed=True))
class Unplace:
    what: ShadowedResource
