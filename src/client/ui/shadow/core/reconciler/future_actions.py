from dataclasses import dataclass

from src.client.ui.shadow.core.props.shadow_node import ShadowNode
from src.client.ui.shadow.core.reconciler.resource import ShadowedResource


@dataclass
class Create[Node: ShadowNode]:
    next: Node


@dataclass
class Update[Node: ShadowNode]:
    existing: ShadowedResource[Node]
    next: Node

    @property
    def props(self):
        return self.existing.diff(self.next)


@dataclass
class Recreate[Node: ShadowNode]:
    old: ShadowedResource[Node]
    next: Node

    @property
    def props(self):
        return self.next._props


@dataclass
class Place[Node: ShadowNode]:
    what: Update[Node] | Recreate[Node] | Create[Node]


@dataclass
class Replace[Node: ShadowNode]:
    replaces: ShadowedResource[Node]
    with_what: Update[Node] | Recreate[Node] | Create[Node]


@dataclass
class Unplace[Node: ShadowNode]:
    what: ShadowedResource[Node]
