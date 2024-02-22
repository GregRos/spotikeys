from typing import Literal

Code = Literal[
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

key_labels = {
    "0": "🄌",
    "1": "➊",
    "2": "➋",
    "3": "➌",
    "4": "➍",
    "5": "➎",
    "6": "➏",
    "7": "➐",
    "8": "➑",
    "9": "➒",
    "*": "⊛",
    "+": "⊞",
    "-": "⊟",
    "/": "⊘",
    "enter": "⏎",
}


class Command:
    code: Code
    hotkey: str | [str, str]

    def __init__(self, command: Code, hotkey: str):
        self.code = command
        self.hotkey = hotkey

    def __str__(self):
        return f"{format_key(self.hotkey)} {self.code}"


def format_key(key: str | [str, str]) -> str:
    if isinstance(key, str):
        return key
    else:
        return f"{key[0]} ⋈ {key[1]}"
