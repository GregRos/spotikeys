from datetime import datetime
from typing import Literal, Tuple

Code = Literal[
    "show_status",
    "hide_status",
    "next_track",
    "prev_track",
    "play_pause",
    "loop_track",
    "seek_fwd",
    "seek_back",
    "rewind_context",
    "repeat_track",
    "love",
    "spin_this_in_last",
    "spin_this_in_new",
    "volume_up",
    "volume_down",
    "volume_max",
    "volume_mute",
    "redo",
    "undo",
    "cancel",
    "rewind_this",
    "next_multi",
    "prev_multi",
]

code_labels: dict[Code, str] = {
    "next_track": "⏩",
    "prev_track": "⏪",
    "play_pause": "⏯️",
    "loop_track": "🔂",
    "seek_fwd": "⬅️",
    "seek_back": "➡️",
    "love": "❤️",
    "spin_this_in_last": "🔄",
    "spin_this_in_new": "🔄*",
    "cancel": "❌",
    "volume_up": "🔉",
    "volume_down": "🔈",
    "volume_max": "🔊",
    "volume_mute": "🔇",
    "undo": "↩️",
    "redo": "↪️",
    "next_multi": "⏭️",
    "prev_multi": "⏮️",
    "rewind_context": "⏫",
    "show_status": "📊",
    "hide_status": "🌫️",
}

type Hotkey = str | Tuple[str, str]

key_labels: dict[str, str] = {
    "0": "0️⃣",
    "1": "1️⃣",
    "2": "2️⃣",
    "3": "3️⃣",
    "4": "4️⃣",
    "5": "5️⃣",
    "6": "6️⃣",
    "7": "7️⃣",
    "8": "8️⃣",
    "9": "9️⃣",
    "*": "*️⃣️",
    "+": "➕",
    "-": "➖",
    "/": "➗",
    "enter": "↩️",
    ".": "●",
}


class Command:
    code: Code

    def __init__(self, command: Code):
        self.code = command

    @property
    def cmd_label(self):
        return code_labels[self.code]

    def __str__(self):
        return f"{self.cmd_label}"

    def to_received(self, key: Hotkey):
        return ReceivedCommand(self, key)


class ReceivedCommand(Command):
    def __init__(self, command: Command, key: Hotkey):
        super().__init__(command.code)
        self.key = key
        self.received = datetime.now()

    @property
    def key_label(self):
        def get_label(k):
            return key_labels[k.replace("num ", "")]

        keys = self.key if isinstance(self.key, tuple) else (self.key,)
        return "➿".join(get_label(k) for k in keys)

    def __str__(self):
        return f"{self.cmd_label} {self.key_label}"
