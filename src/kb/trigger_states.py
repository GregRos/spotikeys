from dataclasses import dataclass, field
from src.commanding.commands import Command


@dataclass()
class TriggerStates:
    down: Command | None = field(default=None)
    up: Command | None = field(default=None)
    suppress: bool = field(default=True)

    def __str__(self):
        parts = []
        if self.down:
            parts.append(f"↓{self.down.title}")
        if self.up:
            parts.append(f"↑{self.up.title}")
        return " ".join(parts)
