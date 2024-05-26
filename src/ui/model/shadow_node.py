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
    PValues,
    PDict,
    PSection,
)
from pydantic import BaseModel, ConfigDict, Field

from src.ui.model.prop_value import PValue


class InitPropsBase(TypedDict):
    key: Annotated[NotRequired[str], Prop(no_value="")]


class ShadowProps(InitPropsBase):
    children: Annotated[NotRequired[tuple[Self, ...]], Prop(no_value=())]


class ShadowNode:
    _props: PValues

    @classmethod
    def node_name(cls) -> str:
        return cls.__name__

    @property
    def type_name(self) -> str:
        return self.__class__.node_name()

    def __init_subclass__(cls) -> None:
        props = AnnotationReader(cls).props = PSection(
            recurse=True, name=cls.node_name()
        ).merge_class(cls)
        original_post_init = getattr(cls, "__post_init__", None)

        def init_props(self):
            original_post_init(self) if original_post_init else None
            self.props = props.with_values({})

        setattr(cls, "__post_init__", init_props)

    def __repr__(self) -> str:
        existing_key = self.key
        props = self._props.__repr__()
        return f"{self.type_name}({props})"

    @property
    def key(self) -> str:
        x = self._props.get("key")
        assert isinstance(x, PValue)
        return x.value

    @abstractmethod
    def _copy(self, **overrides: Any) -> Self: ...
