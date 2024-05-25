from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass(frozen=True)
class Font:
    family: str
    size: int
    style: str = Field(default="normal")

    def to_tk(self):
        return (self.family, self.size, self.style)
