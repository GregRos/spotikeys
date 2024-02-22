import ctypes
from datetime import datetime
from time import sleep

import keyboard

from src.commands import Command, ReceivedCommand
from src.shortcuts.buttons import create_layout
from ui.floating_tooltip import FloatingTooltip

ctypes.windll.shcore.SetProcessDpiAwareness(1)
_tt = FloatingTooltip()


def execute_command(cmd: ReceivedCommand):
    print(f"{datetime.now()} Received command: {cmd}")
    _tt.set_text(cmd.cmd_label, cmd.key_label)
    _tt.show((-250, -250))
    _tt.hide(3)


layout = create_layout(lambda cmd: execute_command(cmd))
layout.register()
keyboard.wait("esc")
