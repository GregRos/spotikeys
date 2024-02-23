import threading
from typing import Callable

import keyboard
from keyboard import KeyboardEvent

from src.shortcuts.labels import key_labels


class Hotkey:
    last_emitted: KeyboardEvent | None = None
    _lock = threading.Lock()
    _registered: Callable[[], None] | None = None

    def __init__(
        self,
        key: str,
        on_down: Callable[[KeyboardEvent], None],
        on_up: Callable[[KeyboardEvent], None] | None = None,
    ):
        self.key = key
        self.on_down = on_down
        self.on_up = on_up

    @property
    def label(self):
        return key_labels.get(self.key, self.key)

    def on_key(self, e: KeyboardEvent):
        with self._lock:
            if (e.is_keypad) != ("num" in self.key):
                return True
            if e.event_type == "up":
                self.last_emitted = None
                if self.on_up:
                    self.on_up(e)
            elif self.last_emitted and e.time - self.last_emitted.time < 1:
                return False
            else:
                self.last_emitted = e
                self.on_down(e)
            return False

    @property
    def hook_key(self):
        return "enter" if self.key == "num enter" else self.key

    def __enter__(self):
        if self._registered:
            return
        self._registered = keyboard.hook_key(
            self.hook_key,
            suppress=True,
            callback=self.on_key,
        )

    def __exit__(self):
        if self._registered:
            keyboard.unhook(self._registered)
            self._registered = None
