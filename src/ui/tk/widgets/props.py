from src.ui.model.prop_def import Prop
from src.ui.model.shadow_node import ShadowProps
from src.ui.tk.font import Font


from typing import Annotated, Literal, NotRequired


class WidgetProps(ShadowProps):
    text: Annotated[NotRequired[str], Prop(default=" ", parent="configure")]
    font: Annotated[
        NotRequired[Font],
        Prop(default=Font("Courier New", 18, "normal"), parent="configure"),
    ]
    borderwidth: Annotated[NotRequired[int], Prop(default=0, parent="configure")]
    background: Annotated[NotRequired[str], Prop(default="#000001", parent="configure")]
    foreground: Annotated[NotRequired[str], Prop(default="#ffffff", parent="configure")]
    justify: Annotated[NotRequired[str], Prop(default="center", parent="configure")]
    relief: Annotated[NotRequired[str], Prop(default="solid", parent="configure")]


class PackProps(ShadowProps):
    ipadx: Annotated[NotRequired[int], Prop(default=0)]
    ipady: Annotated[NotRequired[int], Prop(default=0)]
    fill: Annotated[
        NotRequired[Literal["both", "x", "y", "none"]], Prop(default="none")
    ]
