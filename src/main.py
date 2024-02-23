import ctypes
from datetime import datetime
from time import sleep

import keyboard

from hotkeys import Layout
from media_keys_layout import init_layout


ctypes.windll.shcore.SetProcessDpiAwareness(1)
layout = Layout("media_keys", lambda cmd: print(cmd))
init_layout(layout)
with layout:
    keyboard.wait("esc")
