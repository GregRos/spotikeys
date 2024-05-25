from src.ui.model.props.single.prop_def import PropDef
from src.ui.model.shadow_node import ShadowProps
from src.ui.tk.font import Font


from typing import Annotated, Literal, NotRequired


class WidgetProps(ShadowProps):
    text: Annotated[NotRequired[str], PropDef(default=" ", parent="configure")]
    font: Annotated[
        NotRequired[Font],
        PropDef(default=Font("Courier New", 18, "normal"), parent="configure"),
    ]
    borderwidth: Annotated[NotRequired[int], PropDef(default=0, parent="configure")]
    background: Annotated[
        NotRequired[str], PropDef(default="#000001", parent="configure")
    ]
    foreground: Annotated[
        NotRequired[str], PropDef(default="#ffffff", parent="configure")
    ]
    justify: Annotated[NotRequired[str], PropDef(default="center", parent="configure")]
    relief: Annotated[NotRequired[str], PropDef(default="solid", parent="configure")]


class PackProps(ShadowProps):
    ipadx: Annotated[NotRequired[int], PropDef(default=0)]
    ipady: Annotated[NotRequired[int], PropDef(default=0)]
    fill: Annotated[
        NotRequired[Literal["both", "x", "y", "none"]], PropDef(default="none")
    ]
