import threading
from typing import Literal, Callable, Tuple

import keyboard
from keyboard import KeyboardEvent

from src.commands import Command, ReceivedCommand


class Hotkey:
    last_emitted: KeyboardEvent | None = None
    _lock = threading.Lock()
    _registered: Callable[[], None] | None = None

    def __init__(
        self, key: str, on_down: Callable[[], None], on_up: Callable[[], None] = None
    ):
        self.key = key
        self.on_down = on_down
        self.on_up = on_up

    def on_key(self, e: KeyboardEvent):
        with self._lock:
            if (e.is_keypad) != ("num" in self.key):
                return True
            if e.event_type == "up":
                self.last_emitted = None
                if self.on_up:
                    self.on_up()
            elif self.last_emitted and e.time - self.last_emitted.time < 1:
                return False
            else:
                self.last_emitted = e
                self.on_down()
            return False

    @property
    def hook_key(self):
        return "enter" if self.key == "num enter" else self.key

    def register(self):
        if self._registered:
            return
        self._registered = keyboard.hook_key(
            self.hook_key,
            suppress=True,
            callback=self.on_key,
        )

    def unregister(self):
        if self._registered:
            keyboard.unhook(self._registered)
            self._registered = None


class Layout:
    def __init__(self, name: str, send: Callable[[ReceivedCommand], None]):
        self._hotkeys = []
        self._on_register = []
        self._on_unregister = []
        self.name = name
        self._send = send

    def add(self, hotkey: Hotkey):
        self._hotkeys.append(hotkey)
        return self

    def bind(
        self,
        key: str,
        command: Command,
        other_command: Command | None = None,
    ):
        def on_key():
            if keyboard.is_pressed("num 0"):
                if other_command:
                    self._send(command.to_received(key))
            else:
                self._send(command.to_received(key))

        hotkey = Hotkey(key, on_key)
        self._hotkeys.append(hotkey)
        return self

    def register(self):
        for hotkey in self._hotkeys:
            hotkey.register()

    def unregister(self):
        for hotkey in self._hotkeys:
            hotkey.unregister()


def create_layout(sender: Callable[[ReceivedCommand], None]):
    layout = Layout("media", sender)

    num0 = Hotkey(
        "num 0",
        lambda: sender(Command("show_status").to_received("num 0")),
        lambda: sender(Command("hide_status").to_received("num 0")),
    )

    numdot = Hotkey(
        ".",
        lambda: None,
        lambda: None,
    )

    return (
        layout.add(num0)
        .add(numdot)
        .bind("num -", Command("volume_down"))
        .bind("num *", Command("volume_mute"))
        .bind("num /", Command("volume_max"))
        .bind("num 1", Command("seek_back"))
        .bind("num 2", Command("loop_track"))
        .bind("num 3", Command("seek_fwd"))
        .bind("num 4", Command("prev_track"), Command("prev_multi"))
        .bind("num 5", Command("play_pause"))
        .bind("num 6", Command("next_track"), Command("next_multi"))
        .bind("num 7", Command("undo"))
        .bind("num 8", Command("love"))
        .bind("num 9", Command("redo"))
        .bind("num enter", Command("cancel"), Command("spin_this_in_last"))
        .bind("num +", Command("volume_up"), Command("spin_this_in_new"))
    )
