from src.client.ui.shadow.model.props.single.prop_def import PropDef
from src.client.ui.shadow.model.nodes.shadow_node import ShadowProps
from src.client.ui.values.font import Font


from typing import Annotated, Literal, NotRequired


class WidgetProps(ShadowProps):
    text: Annotated[NotRequired[str], PropDef(default=" ")]
    font: Annotated[
        NotRequired[Font], PropDef(default=Font("Courier New", 18, "normal"))
    ]
    borderwidth: Annotated[NotRequired[int], PropDef(default=0)]
    background: Annotated[NotRequired[str], PropDef(default="#000001")]
    foreground: Annotated[NotRequired[str], PropDef(default="#ffffff")]
    justify: Annotated[NotRequired[str], PropDef(default="center")]
    relief: Annotated[NotRequired[str], PropDef(default="solid")]


class PackProps(ShadowProps):
    ipadx: Annotated[NotRequired[int], PropDef(default=0)]
    ipady: Annotated[NotRequired[int], PropDef(default=0)]
    fill: Annotated[
        NotRequired[Literal["both", "x", "y", "none"]], PropDef(default="none")
    ]
