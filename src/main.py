import ctypes
from datetime import datetime
from time import sleep

import keyboard

from media_keys_layout import create_layout


ctypes.windll.shcore.SetProcessDpiAwareness(1)

layout = create_layout(lambda cmd: execute_command(cmd))
layout.register()
keyboard.wait("esc")
