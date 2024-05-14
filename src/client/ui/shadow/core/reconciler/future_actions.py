from dataclasses import dataclass

from src.client.ui.shadow.core.props.operators import diff
from src.client.ui.shadow.core.reconciler.shadow_node import ShadowNode
from src.client.ui.shadow.core.reconciler.resource import ShadowedResource


@dataclass
class Create:
    next: ShadowNode


@dataclass
class Update:
    existing: ShadowedResource
    next: ShadowNode

    @property
    def props(self):
        return diff(self.existing.node._props, self.next._props)


@dataclass
class Recreate:
    old: ShadowedResource
    next: ShadowNode

    @property
    def props(self):
        return self.next._props


@dataclass
class Place:
    what: Update | Recreate | Create


@dataclass
class Replace:
    replaces: ShadowedResource
    with_what: Update | Recreate | Create


@dataclass
class Unplace:
    what: ShadowedResource
