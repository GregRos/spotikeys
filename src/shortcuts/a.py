from typing import Literal

import keyboard

command = Literal[
    "next",
    "prev",
    "play/pause",
    "restart_track",
    "rewind_context",
    "love",
    "spin_this",
    "volume_up",
    "volume_down",
    "mute",
    "power_next",
    "power_prev",
    "super_next",
    "super_prev",
    "cancel",
    "seek_prev",
    "seek_next",
]

def install():
    all = [
        keyboard.add_hotkey(
            "num plus",
            suppress=True,
            callback=lambda: keyboard.send("volume up")
        ),
        keyboard.add_hotkey(
            "num 0 + num 1",
            suppress=True,
            callback=lambda: keyboard.write("=1+1")
        ),
        keyboard.add_hotkey(
            "num 1",
            suppress=True,
            callback=lambda: keyboard.write("2"),
        ),
        keyboard.add_hotkey(
            "num 6",
            suppress=True,
            callback=lambda: keyboard.write("2"),
        ),
        keyboard.add_hotkey(
            "num 4",
            suppress=True,
            callback=lambda: keyboard.write("2"),
        ),
    ]

install()

keyboard.wait("esc")
