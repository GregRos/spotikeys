from pydantic.dataclasses import dataclass


@dataclass
class Device:
    id: str
    is_active: bool
    is_private_session: bool
    is_restricted: bool
    name: str
    type: str
    volume_percent: int
    supports_volume: bool

    def __str__(self):
        return f"{self.name} ({self.type}) {self.volume_percent}%"
