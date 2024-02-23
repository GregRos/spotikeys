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