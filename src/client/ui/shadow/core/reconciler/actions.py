from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

from src.client.ui.shadow.core.reconciler.record import ResourceRecord
from src.client.ui.shadow.core.props.shadow_node import ShadowNode


@dataclass
class Create[Node: ShadowNode, Resource]:
    next: Node


@dataclass
class Update[Node: ShadowNode, Resource]:
    existing: ResourceRecord[Node, Resource]
    next: Node


@dataclass
class Recreate[Node: ShadowNode, Resource]:
    old: ResourceRecord[Node, Resource]
    next: Node


@dataclass
class Place[Node: ShadowNode, Resource]:
    what: Update[Node, Resource] | Recreate[Node, Resource] | Create[Node, Resource]


@dataclass
class Replace[Node: ShadowNode, Resource]:
    replaces: ResourceRecord[Node, Resource]
    with_what: (
        Update[Node, Resource] | Recreate[Node, Resource] | Create[Node, Resource]
    )


@dataclass
class Unplace[Node: ShadowNode, Resource]:
    what: ResourceRecord[Node, Resource]


class ReconcileActions[Node: ShadowNode, Resource]:

    @abstractmethod
    def create(self, node: Node) -> Resource: ...
    @abstractmethod
    def destroy(self, existing: ResourceRecord[Node, Resource]) -> None: ...

    @abstractmethod
    def update(self, existing: ResourceRecord[Node, Resource], next: Node) -> None: ...

    @abstractmethod
    def unplace(self, existing: ResourceRecord[Node, Resource]) -> None: ...

    @abstractmethod
    def replace(
        self,
        existing: ResourceRecord[Node, Resource],
        next: ResourceRecord[Node, Resource],
    ) -> None: ...

    @abstractmethod
    def place(self, record: ResourceRecord[Node, Resource]) -> None: ...
