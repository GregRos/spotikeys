from datetime import datetime
from threading import Lock
from typing import Callable
import keyboard


class EventEater[Event]:
    _when_enter: datetime | None
    _lock = Lock()

    def __init__(
        self,
        should_eat: Callable[[Event], bool],
        set_hook: Callable[[Callable[[Event], bool]], Callable[[], None]],
        max_age: float,
    ):
        self.should_eat = should_eat
        self._registered = None
        self._when_enter = None
        self.set_hook = set_hook
        self.max_age = max_age

    def register(self):
        self._when_enter = datetime.now()
        if self._registered:
            return
        self._registered = self.set_hook(self.on_event)

    def on_event(self, event: Event):
        with self._lock:
            if not self._registered or not self._when_enter:
                return True
            if not self.should_eat(event):
                return True
            time_since_enter = (datetime.now() - self._when_enter).total_seconds()

            if self.should_eat(event):
                self._registered = None
                too_old = time_since_enter > self.max_age
                if too_old:
                    print("too old to eat")
                else:
                    print("Ate")
                return not too_old

            return True


class Keyboard