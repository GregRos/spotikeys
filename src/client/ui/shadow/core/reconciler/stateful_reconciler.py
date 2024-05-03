from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from imghdr import what
from platform import node
from re import T
from typing import (
    Any,
    Callable,
    Literal,
    Protocol,
    TypeVar,
    TypedDict,
    runtime_checkable,
)
from src.client.ui.framework.component import Component, render_recursively
from src.client.ui.shadow.core.base import ShadowNode, ShadowTkWidget


from itertools import groupby, zip_longest
from tkinter import Label, Tk, Widget


@dataclass
class ResourceRecord[Node: ShadowNode, Resource]:
    node: Node
    resource: Resource
    created: datetime = field(default_factory=datetime.now)


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


class ResourceActions[Node: ShadowNode, Resource]:
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


class StatefulReconciler[Node: ShadowNode, Resource]:
    type ReconcileAction = Place[Node, Resource] | Replace[Node, Resource] | Unplace[
        Node, Resource
    ] | Update[Node, Resource]
    type CreateAction = Create[Node, Resource] | Recreate[Node, Resource] | Update[
        Node, Resource
    ]

    _placement: set[Node]
    _key_to_resource: dict[str, ResourceRecord[Node, Resource]]

    def get_compatibility(
        self, prev: Node | ResourceRecord[Node, Resource], next: Node
    ):
        return next.get_compatibility(
            prev.node if isinstance(prev, ResourceRecord) else prev
        )

    def __init__(self, actions: ResourceActions[Node, Resource]) -> None:
        self.actions = actions
        self._ordering = {}
        self._key_to_resource = {}

    def get_reconcile_action(self, prev: Node | None, next: Node | None):

        if not next:
            assert prev, "Neither prev nor next exists"
            record = self._key_to_resource[prev.key]
            return Unplace(record)

        old_next_placement = self._key_to_resource.get(next.key)

        if not prev:
            if not old_next_placement:
                return Place(Create(next))
            if self.get_compatibility(old_next_placement, next) == "recreate":
                return Place(Recreate(old_next_placement, next))
            return Place(Update(old_next_placement, next))

        old_prev_placement = self._key_to_resource[prev.key]

        if prev.key != next.key:
            if not old_next_placement:
                return Replace(old_prev_placement, Create(next))
            if self.get_compatibility(old_next_placement, next) == "recreate":
                return Replace(old_prev_placement, Recreate(old_next_placement, next))
            return Replace(old_prev_placement, Update(old_next_placement, next))

        assert old_next_placement
        if not self.get_compatibility(prev, next) == "recreate":
            return Replace(old_prev_placement, Recreate(old_next_placement, next))
        return Update(old_next_placement, next)

    @staticmethod
    def check_duplicates(rendering: "list[Node]"):
        key_to_nodes = {
            key: list(group) for key, group in groupby(rendering, key=lambda x: x.key)
        }
        messages = {
            key: f"Duplicates for {key} found: {group} "
            for key, group in key_to_nodes
            if len(group) > 1
        }
        if messages:
            raise ValueError(messages)

    def compute_reconcile_actions(self, rendering: list[Node]):
        self.check_duplicates(rendering)
        placed = set[str]()
        for prev, next in zip_longest(self._ordering, rendering, fillvalue=None):
            if not next and prev and prev.key in placed:
                continue
            if next:
                placed.add(next.key)
            yield self.get_reconcile_action(prev, next)

    def do_create_action(self, action: Update[Node, Resource] | Create[Node, Resource]):
        match action:
            case Create(next):
                new_resource = self.actions.create(next)
                return ResourceRecord(next, new_resource)
            case Update(existing, next):
                self.actions.update(existing, next)
                return ResourceRecord(next, existing.resource)
            case _:
                assert False, f"Unknown action: {action}"

    def do_reconcile_action(self, action: ReconcileAction):
        actions = self.actions
        match action:
            case Update(existing, next):
                actions.update(existing, next)
            case Unplace(x):
                self.actions.unplace(x)
            case Place(Recreate(old, next)):
                new_resource = self.do_create_action(Create(next))
                actions.destroy(old)
                actions.place(new_resource)
            case Place(createAction) if not isinstance(createAction, Recreate):
                item = self.do_create_action(createAction)
                actions.place(item)
            case Replace(replaces, Recreate(old, next)):
                item = self.do_create_action(Create(next))
                actions.replace(replaces, item)
                actions.destroy(old)
            case Replace(replaces, createAction) if not isinstance(
                createAction, Recreate
            ):
                item = self.do_create_action(createAction)
                actions.replace(replaces, item)
            case _:
                assert False, f"Unknown action: {action}"

    def reconcile(self, root: "Component[Node]"):
        from src.client.ui.framework.component import Component

        rendering = list(render_recursively("", root))
        reconcile = [*self.compute_reconcile_actions(rendering)]
        for reconcile in reconcile:
            self.do_reconcile_action(reconcile)
