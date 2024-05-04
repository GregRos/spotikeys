from dataclasses import dataclass, field


@dataclass(frozen=True)
class Font:
    family: str
    size: int
    style: str = field(default="normal")

    def to_tk(self):
        return (self.family, self.size, self.style)
