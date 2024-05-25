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


from src.ui.model.annotation_reader import AnnotationReader
from src.ui.model.prop import Prop
from src.ui.model.prop_dict import (
    PropVals,
    PropDict,
    get_sections,
    section,
)
from pydantic import BaseModel, ConfigDict, Field

from src.ui.model.prop_value import PropValue


class InitPropsBase(TypedDict):
    key: Annotated[NotRequired[str], Prop(default="")]


class ShadowProps(InitPropsBase):
    children: Annotated[NotRequired[tuple[Self, ...]], Prop(default=())]


class ShadowNode:
    _props: PropVals

    def __init_subclass__(cls) -> None:
        props = AnnotationReader(cls).props = section(get_sections(cls), recurse=True)
        original_post_init = getattr(cls, "__post_init__", None)

        def init_props(self):
            original_post_init(self) if original_post_init else None
            self.props = props.with_values({})

        setattr(cls, "__post_init__", init_props)

    @property
    def key(self) -> str:
        x = self._props.get("key")
        assert isinstance(x, PropValue)
        return x.value

    @abstractmethod
    def _copy(self, **overrides: Any) -> Self: ...
