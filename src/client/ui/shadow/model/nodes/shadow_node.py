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
from pydantic import BaseModel, ConfigDict, Field


class InitPropsBase(TypedDict):
    key: Annotated[NotRequired[str], PropDef(default="")]


class ShadowProps(InitPropsBase):
    children: Annotated[NotRequired[tuple[Self]], PropDef(default=())]


class ShadowNode:

    def __init__(self, props: PropsDict, /) -> None:
        self._props = props

    @property
    def key(self) -> str:
        return self._props["key"].value

    @abstractmethod
    def _copy(self, **overrides: Any) -> Self: ...
