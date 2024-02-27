import threading
from typing import Callable

import keyboard
from keyboard import KeyboardEvent

from src.client.hotkeys.key import Key


class Hotkey:
    last_emitted: KeyboardEvent | None = None
    _lock = threading.Lock()
    _registered: Callable[[], None] | None = None

    def __init__(
        self,
        key: Key,
        on_down: Callable[[KeyboardEvent], None],
        on_up: Callable[[KeyboardEvent], None] | None = None,
    ):
        self.key = key
        self.on_down = on_down
        self.on_up = on_up

    def on_key(self, e: KeyboardEvent):
        with self._lock:
            if (e.is_keypad) != ("num" in self.key.id):
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

    def __str__(self):
        return self.key.__str__()

    def __enter__(self):
        if self._registered:
            return
        self._registered = keyboard.hook_key(
            self.key.hook_id,
            suppress=True,
            callback=self.on_key,
        )

    def __exit__(self):
        if self._registered:
            keyboard.unhook(self._registered)
            self._registered = None
