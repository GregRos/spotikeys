from typing import Literal, Tuple

from commanding import Command

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

cmd_volume_down = Command("volume_down", "🔈")
cmd_volume_mute = Command("volume_mute", "🔇")
cmd_volume_up = Command("volume_up", "🔊")
cmd_volume_max = Command("volume_max", "🔊")
cmd_seek_bwd = Command("seek_back", "⬅️")
cmd_loop_track = Command("loop_track", "🔂")
cmd_seek_fwd = Command("seek_fwd", "➡️")
cmd_prev_track = Command("prev_track", "⏪")
cmd_play_pause = Command("play_pause", "⏯️")
cmd_next_track = Command("next_track", "⏩")
cmd_undo = Command("undo", "↩️")
cmd_love = Command("love", "❤️")
cmd_redo = Command("redo", "↪️")
cmd_cancel = Command("cancel", "❌️")
cmd_spin_this_in_last = Command("spin_this_in_last", "🔄")

cmd_spin_this_in_new = Command("spin_this_in_new", "🔄*")
cmd_prev_multi = Command("prev_multi", "⏮️")
cmd_next_multi = Command("next_multi", "⏭️")

cmd_show_status = Command("show_status", "📊").local()
cmd_get_status = Command("get_status", "📊")
cmd_hide_status = Command("hide_status", "📊").local()
