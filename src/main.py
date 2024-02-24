import ctypes
from datetime import datetime
from time import sleep

import keyboard
from keys import *
from commands import *
from hotkeys import Layout
from media_keys_layout import init_layout
from manager import command_spotify_manager

ctypes.windll.shcore.SetProcessDpiAwareness(1)
layout = Layout("media_keys", command_spotify_manager.receive)
layout.add_bindings(
    num_dot.bind_off(),
    num_0.bind_up_down(cmd_show_status, cmd_hide_status),
    num_1.bind_numpad(cmd_seek_back),
    num_2.bind_numpad(cmd_loop_track),
    num_3.bind_numpad(cmd_seek_fwd),
    num_4.bind_numpad(cmd_prev_track, cmd_prev_multi),
    num_5.bind_numpad(cmd_play_pause),
    num_6.bind_numpad(cmd_next_track, cmd_next_multi),
    num_7.bind_numpad(cmd_undo),
    num_8.bind_numpad(cmd_love),
    num_9.bind_numpad(cmd_redo),
    num_enter.bind_numpad(cmd_cancel, cmd_spin_this_in_last),
    num_plus.bind_numpad(cmd_volume_up, cmd_spin_this_in_new),
    num_minus.bind_numpad(cmd_volume_down),
    num_asterisk.bind_numpad(cmd_volume_mute),
    num_slash.bind_numpad(cmd_volume_max),
)
with layout:
    keyboard.wait("esc")
