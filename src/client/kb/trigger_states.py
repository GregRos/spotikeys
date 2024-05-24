from src.commanding.commands import Command


from pydantic.dataclasses import dataclass, field


@dataclass()
class TriggerStates:
    down: Command | None = field(default=None)
    up: Command | None = field(default=None)
    suppress: bool = field(default=True)

    def __str__(self):
        parts = []
        if self.down:
            parts.append(f"↓{self.down}")
        if self.up:
            parts.append(f"↑{self.up}")
        return " ".join(parts)
