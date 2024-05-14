from dataclasses import field
from turtle import title
from pydantic import Field


from abc import ABC, abstractmethod
from typing import (
    TYPE_CHECKING,
    Annotated,
    Any,
    ClassVar,
    Literal,
    NotRequired,
    Self,
    TypedDict,
)

from pydantic.dataclasses import dataclass

from src.client.ui.shadow.model.props.single.prop_def import PropDef
from src.client.ui.shadow.model.props.dict.props_dict import PropsDict


class InitPropsBase(TypedDict):
    key: Annotated[NotRequired[str], PropDef()]


class ShadowProps(TypedDict):
    key: Annotated[NotRequired[str], PropDef(default="")]
    children: Annotated[NotRequired[tuple[Self]], PropDef(default=())]


class ShadowNode:
    _props: PropsDict

    def __init__(self, props: PropsDict = PropsDict({}), /) -> None:
        self._props = props

    @property
    def key(self) -> str:
        return self._props["key"]

    @abstractmethod
    def _copy(self, **overrides: Any) -> Self: ...
