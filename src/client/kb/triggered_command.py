from datetime import date
import datetime
import time

from pydantic import Field
from src.client.kb.key import Key
from src.client.kb.key_combination import KeyCombination
from src.commanding.commands import Command


from pydantic.dataclasses import dataclass, field
from typing import Any, Awaitable, Callable, Coroutine, Literal, TypeGuard


@dataclass()
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
        modifiers = f"[{self.modifiers}]" if self.modifiers else ""
        return f"{self.trigger.label}{modifiers} ➜  {self.command.label}"

    async def execute_async[T](self, executor: Callable[[], Awaitable[T]]):
        start = time.time()
        try:
            result = await executor()
            end = time.time()
            return OkayCommand(self, end - start, result)
        except Exception as e:
            end = time.time()
            return FailedCommand(self, end - start, e)

    def execute(self, executor: Callable[[], Any]):
        start = time.time()
        try:
            result = executor()
            end = time.time()
            return OkayCommand(self, end - start, result)
        except Exception as e:
            end = time.time()
            return FailedCommand(self, end - start, e)

    def __str__(self):
        return self.label


@dataclass()
class OkayCommand[T]:
    success: Literal[True] = Field(default=True, init=False)
    triggered: TriggeredCommand
    command: Command = Field(init=False)
    duration: float
    result: T

    def __post_init__(self):
        self.command = self.triggered.command


@dataclass
class FailedCommand:
    success: Literal[False] = Field(default=False, init=False)
    triggered: TriggeredCommand
    duration: float
    exception: Exception
