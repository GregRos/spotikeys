from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Callable, Literal, Self

from pydantic import BaseModel


from src.ui.model.props.dict.props_dict import PropVals, PropsDict
from src.ui.model.shadow_node import ShadowNode, ShadowProps

type Compat = Literal["update", "replace", "recreate"]


class ShadowedResource[Node: ShadowNode](ABC):

    @staticmethod
    @abstractmethod
    def node_type() -> type[Node]: ...
    @abstractmethod
    def is_same_resource(self, other: Self) -> bool: ...

    def __eq__(self, value: object) -> bool:
        return (
            isinstance(value, self.__class__)
            and self.node == value.node
            and self.is_same_resource(value)
        )

    def props(self, other: Node | None = None) -> PropVals:
        a = self.node._props
        if not other:
            return a
        return a.diff(other._props)

    def __init__(self, node: Node):
        self.node = node

    @abstractmethod
    def migrate(self, node: Node) -> Self: ...

    @abstractmethod
    def destroy(self) -> None: ...

    @abstractmethod
    def update(self, props: PropVals) -> None: ...

    @abstractmethod
    def place(self) -> None: ...

    @abstractmethod
    def unplace(self) -> None: ...

    @abstractmethod
    def replace(self, other: Self) -> None: ...

    @abstractmethod
    def get_compatibility(self, other: Node) -> Compat: ...
