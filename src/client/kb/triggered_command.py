from datetime import date
import datetime
import time
from src.client.kb.key import Key
from src.client.kb.key_combination import KeyCombination
from src.commanding.commands import Command


from dataclasses import dataclass
from typing import Literal


@dataclass
class TriggeredCommand:
    command: Command
    trigger: Key
    event: Literal["down", "up", None]
    modifiers: KeyCombination

    def __post_init__(self):
        self.timestamp = time.time()

    @property
    def code(self):
        return self.command.code

    @property
    def label(self):
        return f"{self.trigger.label}{self.modifiers} ➜  {self.command.label}"

    def __str__(self):
        return self.label
