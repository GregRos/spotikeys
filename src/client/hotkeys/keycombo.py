from datetime import time
import datetime
from logging import getLogger
import threading
from time import sleep
from typing import Callable

from keyboard import KeyboardEvent
import keyboard
import mouse
from mouse import ButtonEvent
from src.client.kb.key import Key, ModifiedKey

logger = getLogger("keyboard")


class KeyCombo:
    last_emitted: KeyboardEvent | None = None
    _lock = threading.Lock()
    _registered: Callable[[], None] | None = None

    def __init__(
        self,
        key: Key | ModifiedKey,
        on_press: Callable[[], None],
        on_press_leftmouse: Callable[[], None] | None = None,
        on_press_rightmouse: Callable[[], None] | None = None,
    ):
        self.key = key
        self._on_press = on_press
        self._on_press_leftmouse = on_press_leftmouse
        self._on_press_rightmouse = on_press_rightmouse
        self._release_eater = None
        self._release_eater_when = None

    def _eat_release(self):
        release_eater = self._release_eater
        self._release_eater = None
        try:
            mouse.unhook(release_eater)
        except Exception as e:
            if "not in the list" in str(e):
                return False
            logger.error("Failed to unhook release eater", exc_info=True)
            return False
        if (
            self._release_eater_when
            and (datetime.datetime.now() - self._release_eater_when).total_seconds()
            > 30
        ):
            print("too old to eat")
            return False
        print("Ate release")

        return False

    def on_press(self):
        sleep(0.1)
        with self._lock:
            if self._on_press_leftmouse and mouse.is_pressed("left"):
                self._release_eater = self._release_eater or mouse.on_button(
                    self._eat_release, buttons=["left", "left"], types=["up"]
                )
                self._release_eater_when = datetime.datetime.now()
                sleep(0.2)
                self._on_press_leftmouse()
            elif self._on_press_rightmouse and mouse.is_pressed("right"):
                self._release_eater = self._release_eater or mouse.on_button(
                    self._eat_release, buttons=["right", "left"], types=["up"]
                )
                self._release_eater_when = datetime.datetime.now()
                sleep(0.2)
                self._on_press_rightmouse()
            else:
                self._on_press()

        return False

    def __str__(self):
        return self.key.__str__()

    def __enter__(self):
        if self._registered:
            return
        self._registered = keyboard.add_hotkey(
            self.key.hotkey_id,
            suppress=True,
            callback=self.on_press,
        )

    def __exit__(self):
        if self._registered:
            keyboard.unhook(self._registered)
            self._registered = None
