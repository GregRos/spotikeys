from dataclasses import dataclass, field
from datetime import date
import datetime
import time
import traceback

from src.kb.key import Key
from src.kb.key_combination import KeyCombination
from src.commanding.commands import Command


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
    def emoji(self):
        modifiers = f"{self.modifiers}" if self.modifiers else ""
        return f"{self.trigger.label}{modifiers}➜ {self.command.emoji}"

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
            print(traceback.format_exc())
            return FailedCommand(self, end - start, e)

    def __str__(self):
        return f"{self.trigger} {self.modifiers} ➤ {self.command}"

    def __repr__(self):
        return f"TriggeredCommand({self.__str__()})"


@dataclass()
class OkayCommand[T]:
    success: Literal[True] = field(default=True, init=False)
    triggered: TriggeredCommand
    command: Command = field(init=False)
    duration: float
    result: T

    def __post_init__(self):
        self.command = self.triggered.command


@dataclass(repr=False)
class FailedCommand:
    success: Literal[False] = field(default=False, init=False)
    triggered: TriggeredCommand
    duration: float
    exception: Exception

    def __repr__(self):
        formatted = "".join(
            map(lambda x: f"∙ {x}", traceback.format_exception(self.exception))
        )
        return f"❌ {self.triggered} {self.duration:.2f}s\n{formatted}"

    @property
    def command(self):
        return self.triggered.command
