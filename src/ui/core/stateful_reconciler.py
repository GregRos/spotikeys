import logging
from typing import (
    Callable,
    Iterable,
)
from src.ui.model.resource import (
    ShadowedResource,
)
from src.ui.core.future_actions import (
    Create,
    Recreate,
    Replace,
    Unplace,
    Update,
    Place,
)
from src.ui.model.shadow_node import ShadowNode


from itertools import groupby, zip_longest

logger = logging.getLogger("reconciler")


class StatefulReconciler[Node: ShadowNode]:

    type ReconcileAction = Place | Replace | Unplace | Update
    type CreateAction = Create | Recreate | Update

    _placement: tuple[ShadowNode, ...]
    _key_to_resource: dict[str, ShadowedResource]

    def __init__(
        self,
        resource_type: type[ShadowedResource[Node]],
        create: Callable[[Node], ShadowedResource[Node]],
    ):
        self._placement = ()
        self._key_to_resource = {}
        self.create = create
        self.resource_type = resource_type

    @property
    def node_type(self) -> type[ShadowNode]:
        return self.resource_type.node_type()

    def _get_reconcile_action(self, prev: ShadowNode | None, next: ShadowNode | None):

        if not next:
            assert prev, "Neither prev nor next exists"
            record = self._key_to_resource[prev.key]
            return Unplace(record)

        old_next_placement = self._key_to_resource.get(next.key)

        if not prev:
            if not old_next_placement:
                return Place(Create(next))
            if old_next_placement.get_compatibility(next) == "recreate":
                return Place(Recreate(old_next_placement, next))
            return Place(Update(old_next_placement, next))

        old_prev_placement = self._key_to_resource[prev.key]

        if prev.key != next.key:
            if not old_next_placement:
                return Replace(old_prev_placement, Create(next))
            if old_next_placement.get_compatibility(next) == "recreate":
                return Replace(old_prev_placement, Recreate(old_next_placement, next))
            return Replace(old_prev_placement, Update(old_next_placement, next))

        assert old_next_placement
        if old_next_placement.get_compatibility(next) == "recreate":
            return Replace(old_prev_placement, Recreate(old_next_placement, next))
        return Update(old_next_placement, next)

    @staticmethod
    def _check_duplicates(rendering: Iterable[ShadowNode]):
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

    def compute_reconcile_actions(self, rendering: Iterable[ShadowNode]):
        self._check_duplicates(rendering)
        placed = set[str]()
        for prev, next in zip_longest(self._placement, rendering, fillvalue=None):
            if not next and prev and prev.key in placed:
                continue
            if next:
                placed.add(next.key)
            yield self._get_reconcile_action(prev, next)

    def _do_create_action(self, action: Update | Create):
        match action:
            case Create(next):
                new_resource = self.create(next)  # type: ignore
                new_resource.update(next._props)
                self._key_to_resource[next.key] = new_resource
                return new_resource
            case Update(existing, next):
                diff = existing.props(next)
                existing.update(diff)
                return existing.migrate(next)
            case _:
                assert False, f"Unknown action: {action}"

    def _do_reconcile_action(self, action: ReconcileAction):
        logger.info(f"Reconcile action: {action}")
        match action:
            case Update(existing, next):
                self._do_create_action(action)
            case Unplace(existing):
                existing.unplace()
            case Place(Recreate(old, next)):
                new_resource = self._do_create_action(Create(next))
                old.destroy()
                new_resource.place()
            case Place(createAction) if not isinstance(createAction, Recreate):
                resource = self._do_create_action(createAction)
                resource.place()
            case Replace(existing, Recreate(old, next)):
                resource = self._do_create_action(Create(next))
                existing.replace(resource)
                old.destroy()
            case Replace(existing, createAction) if not isinstance(
                createAction, Recreate
            ):
                resource = self._do_create_action(createAction)
                existing.replace(resource)
            case _:
                assert False, f"Unknown action: {action}"

    def reconcile(self, rendering: tuple[ShadowNode, ...]):
        reconcile = [*self.compute_reconcile_actions(rendering)]
        for reconcile in reconcile:
            self._do_reconcile_action(reconcile)
        self._placement = rendering
