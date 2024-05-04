from abc import abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from imghdr import what
import logging
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
from src.client.ui.shadow.core.reconciler.actions import (
    Create,
    Recreate,
    Replace,
    ReconcileActions,
    Unplace,
    Update,
    Place,
)
from src.client.ui.shadow.core.reconciler.record import ResourceRecord
from src.client.ui.shadow.core.props.shadow_node import ShadowNode
from src.client.ui.shadow.tk.widgets.widget import SwTkWidget


from itertools import groupby, zip_longest
from tkinter import Label, Tk, Widget

logger = logging.getLogger("reconciler")


class StatefulReconciler[Node: ShadowNode, Resource]:
    type ReconcileAction = Place[Node, Resource] | Replace[Node, Resource] | Unplace[
        Node, Resource
    ] | Update[Node, Resource]
    type CreateAction = Create[Node, Resource] | Recreate[Node, Resource] | Update[
        Node, Resource
    ]

    _placement: list[Node]
    _key_to_resource: dict[str, ResourceRecord[Node, Resource]]

    def _get_compatibility(
        self, prev: Node | ResourceRecord[Node, Resource], next: Node
    ):
        return next.get_compatibility(
            prev.node if isinstance(prev, ResourceRecord) else prev
        )

    def __init__(self, actions: ReconcileActions[Node, Resource]) -> None:
        self.actions = actions
        self._placement = set()
        self._key_to_resource = {}

    def _get_reconcile_action(self, prev: Node | None, next: Node | None):

        if not next:
            assert prev, "Neither prev nor next exists"
            record = self._key_to_resource[prev.key]
            return Unplace(record)

        old_next_placement = self._key_to_resource.get(next.key)

        if not prev:
            if not old_next_placement:
                return Place(Create(next))
            if self._get_compatibility(old_next_placement, next) == "recreate":
                return Place(Recreate(old_next_placement, next))
            return Place(Update(old_next_placement, next))

        old_prev_placement = self._key_to_resource[prev.key]

        if prev.key != next.key:
            if not old_next_placement:
                return Replace(old_prev_placement, Create(next))
            if self._get_compatibility(old_next_placement, next) == "recreate":
                return Replace(old_prev_placement, Recreate(old_next_placement, next))
            return Replace(old_prev_placement, Update(old_next_placement, next))

        assert old_next_placement
        if not self._get_compatibility(prev, next) == "update":
            return Replace(old_prev_placement, Recreate(old_next_placement, next))
        return Update(old_next_placement, next)

    @staticmethod
    def _check_duplicates(rendering: "list[Node]"):
        key_to_nodes = {
            key: list(group) for key, group in groupby(rendering, key=lambda x: x.key)
        }
        messages = {
            key: f"Duplicates for {key} found: {group} "
            for key, group in key_to_nodes.items()
            if len(group) > 1
        }
        if messages:
            raise ValueError(messages)

    def compute_reconcile_actions(self, rendering: list[Node]):
        self._check_duplicates(rendering)
        placed = set[str]()
        for prev, next in zip_longest(self._placement, rendering, fillvalue=None):
            if not next and prev and prev.key in placed:
                continue
            if next:
                placed.add(next.key)
            yield self._get_reconcile_action(prev, next)

    def _do_create_action(
        self, action: Update[Node, Resource] | Create[Node, Resource]
    ):
        match action:
            case Create(next):
                new_resource = self.actions.create(next)
                record = ResourceRecord(next, new_resource)
                self._key_to_resource[next.key] = record
                return record
            case Update(existing, next):
                self.actions.update(existing, next)
                return ResourceRecord(next, existing.resource)
            case _:
                assert False, f"Unknown action: {action}"

    def _do_reconcile_action(self, action: ReconcileAction):
        actions = self.actions
        logger.info(f"Reconcile action: {action}")
        match action:
            case Update(existing, next):
                actions.update(existing, next)
            case Unplace(x):
                actions.unplace(x)
            case Place(Recreate(old, next)):
                new_resource = self._do_create_action(Create(next))
                actions.destroy(old)
                actions.place(new_resource)
            case Place(createAction) if not isinstance(createAction, Recreate):
                item = self._do_create_action(createAction)
                actions.place(item)
            case Replace(replaces, Recreate(old, next)):
                item = self._do_create_action(Create(next))
                actions.replace(replaces, item)
                actions.destroy(old)
            case Replace(replaces, createAction) if not isinstance(
                createAction, Recreate
            ):
                item = self._do_create_action(createAction)
                actions.replace(replaces, item)
            case _:
                assert False, f"Unknown action: {action}"

    def reconcile(self, root: "Component[Node]"):
        from src.client.ui.framework.component import Component

        rendering = list(render_recursively("", root))
        reconcile = [*self.compute_reconcile_actions(rendering)]
        for reconcile in reconcile:
            self._do_reconcile_action(reconcile)
        self._placement = rendering
