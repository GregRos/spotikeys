from dataclasses import dataclass
from src.ui.model.component import Component
from ui.model.shadow_node import ShadowNode


@dataclass(kw_only=True)
class RenderFrame:
    pos: int
    type: type[Component] | type[ShadowNode]
    key: str


class RenderTrace:
    frames: tuple[RenderFrame, ...]

    def __init__(self, *frames: RenderFrame):
        self.frames = frames

    def __add__(self, other: "RenderTrace | RenderFrame") -> "RenderTrace":
        if isinstance(other, RenderFrame):
            return RenderTrace(*self.frames, other)
        return RenderTrace(*self.frames, *other.frames)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, RenderTrace):
            return NotImplemented
        return self.frames == value.frames

    def to_log_string(self) -> str:
        return " -> ".join(f"{f.type.__name__}({f.key})" for f in self.frames)

    def to_uid(self) -> str:
        return " -> ".join(f"{f.type.__name__}({f.key})" for f in self.frames)
