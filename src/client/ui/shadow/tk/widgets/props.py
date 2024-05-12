from src.client.ui.shadow.core.props.props import PropDef
from src.client.ui.shadow.core.props.shadow_node import ShadowProps
from src.client.ui.values.font import Font


from typing import Annotated, Literal


class WidgetProps(ShadowProps):
    text: Annotated[str, PropDef(default=" ")]
    font: Annotated[Font, PropDef(default=Font("Courier New", 18, "normal"))]
    borderwidth: Annotated[int, PropDef(default=0)]
    background: Annotated[str, PropDef(default="#000001")]
    foreground: Annotated[str, PropDef(default="#ffffff")]
    justify: Annotated[str, PropDef(default="center")]
    relief: Annotated[str, PropDef(default="solid")]


class PackProps(ShadowProps):
    ipadx: Annotated[int, PropDef(default=0)]
    ipady: Annotated[int, PropDef(default=0)]
    fill: Annotated[Literal["both", "x", "y", "none"], PropDef(default="none")]
