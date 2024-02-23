import ctypes
from datetime import datetime
from time import sleep

import keyboard

from src.commanding.commands import Command, ReceivedCommand
from ui.floating_tooltip import MediaTooltip

ctypes.windll.shcore.SetProcessDpiAwareness(1)
_tt = MediaTooltip()

layout = create_layout(lambda cmd: execute_command(cmd))
layout.register()
keyboard.wait("esc")
