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
from ui.model.render_trace import RenderTrace


class InitPropsBase(TypedDict):
    key: Annotated[NotRequired[str], Prop(no_value=None)]


class ShadowProps(InitPropsBase):
    children: Annotated[NotRequired[tuple[Self, ...]], Prop(no_value=())]


class ShadowNode:
    _props: PValues
    trace: RenderTrace

    @classmethod
    def node_name(cls) -> str:
        return cls.__name__

    @property
    def type_name(self) -> str:
        return self.__class__.node_name()

    def __init_subclass__(cls) -> None:
        props = AnnotationReader(cls).section = PSection(
            recurse=True, name=cls.node_name()
        ).merge_class(cls)
        original_post_init = getattr(cls, "__post_init__", None)

        def init_props(self):
            original_post_init(self) if original_post_init else None
            self.props = props.with_values({})

        setattr(cls, "__post_init__", init_props)

    def __repr__(self) -> str:
        return self._props.__repr__()

    @property
    def key(self) -> str | None:
        x = self._props.get("key")
        assert not isinstance(x, PValues), "Key should not be a PValues."
        return x.value if x else None

    @property
    def uid(self) -> str:
        assert self.trace, "Trace must exist before calling u_key."
        return self.trace.to_uid()

    @abstractmethod
    def _copy(self, **overrides: Any) -> Self: ...
