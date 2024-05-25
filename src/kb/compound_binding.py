import threading
from typing import Callable, Optional

from keyboard import KeyboardEvent
import keyboard
from src.kb.trigger_states import TriggerStates
from src.kb.triggered_command import TriggeredCommand
from src.kb.key import Key
from src.kb.key_combination import KeyCombination
from src.commanding.commands import Command, CommandLike


class CompoundBinding:
    __match_args__ = ("key", "cases")
    _lock = threading.Lock()

    def __init__(
        self,
        trigger: Key,
        modifiers: dict[KeyCombination, TriggerStates] = {},
    ):
        self.trigger = trigger
        self.modifiers = modifiers.copy()

    def __iter__(self):
        x = sorted(self.modifiers.items(), key=lambda x: x[0])
        return iter(x)

    def __contains__(self, key: Key | None):
        return key in self.modifiers

    def __len__(self):
        return len(self.modifiers)

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, CompoundBinding):
            return False
        return self.trigger == value.trigger and self.modifiers == value.modifiers

    def __hash__(self) -> int:
        return hash(self.trigger) ^ hash(self.modifiers)

    def whens(self, cases: dict[KeyCombination | Key, Command]):
        cases2 = dict(
            (KeyCombination({k}) if isinstance(k, Key) else k, TriggerStates(v))
            for k, v in cases.items()
        )
        return CompoundBinding(self.trigger, {**self.modifiers, **cases2})

    def when(
        self,
        key: Key | KeyCombination,
        down: Command | None = None,
        up: Command | None = None,
        suppress: bool = True,
    ):
        key = KeyCombination({key}) if isinstance(key, Key) else key
        case = TriggerStates(down, up, suppress)
        return CompoundBinding(self.trigger, {**self.modifiers, key: case})

    def handler(
        self, receiver: Callable[[TriggeredCommand], None]
    ) -> Callable[[KeyboardEvent], bool]:
        def on_event(e: KeyboardEvent) -> bool:
            with self._lock:
                if not self.trigger.match_event(e):
                    return True

                p = max(
                    (
                        (combo, triggers)
                        for combo, triggers in self.modifiers.items()
                        if combo.is_pressed()
                    ),
                    key=lambda x: x[0],
                )
                if not p:
                    return True

                combo, triggers = p
                cmd = triggers.down if e.event_type == "down" else triggers.up
                if cmd:
                    receiver(TriggeredCommand(cmd, self.trigger, e.event_type, combo))
                return not triggers.suppress

        return on_event

    def default(
        self,
        down: Command | None = None,
        up: Command | None = None,
        suppress: bool = True,
    ):
        empty = KeyCombination(set())
        case = TriggerStates(down, up, suppress)
        return CompoundBinding(self.trigger, {**self.modifiers, empty: case})
