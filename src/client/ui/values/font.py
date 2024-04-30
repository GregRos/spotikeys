from attr import dataclass


@dataclass
class Font:
    family: str
    size: int
    style: str

    def to_tk(self):
        return (self.family, self.size, self.style)
