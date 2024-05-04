from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable, Literal, Self

from referencing import Resource

from src.client.ui.shadow.core.props.props_map import PropsMap
from src.client.ui.shadow.core.props.shadow_node import ShadowNode

type Compat = Literal["update", "replace", "recreate"]


class ShadowedResource[Node: ShadowNode](ABC):

    @abstractmethod
    def is_same_resource(self, other: Self) -> bool: ...

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, self.__class__)
            and self.node == value.node
            and self.is_same_resource(value)
        )

    def diff(self, other: Node) -> PropsMap:
        return self.node._props.diff(other._props)

    def __init__(self, node: Node):
        self.node = node

    @abstractmethod
    def migrate(self, node: Node) -> Self: ...

    @abstractmethod
    def destroy(self) -> None: ...

    @abstractmethod
    def update(self, props: PropsMap) -> None: ...

    @abstractmethod
    def place(self) -> None: ...

    @abstractmethod
    def unplace(self) -> None: ...

    @abstractmethod
    def replace(self, other: Self) -> None: ...

    @abstractmethod
    def get_compatibility(self, other: Node) -> Compat: ...
