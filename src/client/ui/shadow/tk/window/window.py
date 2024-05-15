from typing import (
    Annotated,
    Any,
    NotRequired,
    Self,
    Unpack,
    override,
)


from src.client.ui.shadow.model.props.single.prop_def import PropDef
from src.client.ui.shadow.model.props.dict.prop_section import PropSection
from src.client.ui.shadow.model.components.component import Component
from src.client.ui.shadow.model.nodes.shadow_node import (
    InitPropsBase,
    ShadowNode,
)
from src.client.ui.shadow.tk.widgets.widget import WidgetNode
from pydantic.dataclasses import dataclass


class WindowProps(InitPropsBase):
    topmost: Annotated[NotRequired[bool], PropDef(section="configure")]
    background: Annotated[NotRequired[str], PropDef(section="attributes")]
    transparent_color: Annotated[NotRequired[str], PropDef(section="attributes")]
    override_redirect: NotRequired[bool]
    alpha: Annotated[NotRequired[float], PropDef(section="attributes")]


class Geometry(InitPropsBase):
    x: int
    y: int
    width: int
    height: int


class SwTkWindow(ShadowNode, Component[WidgetNode]):  # type: ignore

    @PropSection(diff_mode="recursive").section_setter
    def __init__(self, **props: Unpack[WindowProps]): ...

    @PropSection(diff_mode="simple").section_setter
    def geometry(self, **props: Unpack[Geometry]): ...

    @override
    def _copy(self, **overrides: Any) -> Self:
        return self.__class__(**self._props.merge(overrides))


@dataclass(kw_only=True)
class WindowComponent(Component[SwTkWindow]):
    pass
