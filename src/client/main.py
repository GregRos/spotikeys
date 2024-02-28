import ctypes
from datetime import datetime
import logging
from time import sleep
from turtle import setup
from typing import Callable

from colorama import init
import keyboard

from src.client.client_command_handler import ClientCommandHandler
from src.commanding.handler import CommandHandler
from .keys import *
from src.client.received_command import ReceivedCommand
from src.now_playing import MediaStatus
from src.commands import *
from src.client.hotkeys.layout import Layout

from src.log_config import setup_logging

setup_logging()


def create_client(send: CommandHandler[Command, MediaStatus]):
    cmd = ClientCommandHandler(send)
    layout = Layout("media_keys", cmd)
    layout.add_bindings(
        num_dot.bind_off(),
        num_0.bind_up_down(MediaCommands.show_status, MediaCommands.hide_status),
        num_1.bind_numpad(MediaCommands.seek_bwd),
        num_2.bind_numpad(MediaCommands.loop_track),
        num_3.bind_numpad(MediaCommands.seek_fwd),
        num_4.bind_numpad(MediaCommands.prev_track, MediaCommands.prev_multi),
        num_5.bind_numpad(MediaCommands.play_pause),
        num_6.bind_numpad(MediaCommands.next_track, MediaCommands.next_multi),
        num_7.bind_numpad(MediaCommands.undo),
        num_8.bind_numpad(MediaCommands.love),
        num_9.bind_numpad(MediaCommands.redo),
        num_enter.bind_numpad(MediaCommands.cancel, MediaCommands.spin_this_in_last),
        num_plus.bind_numpad(MediaCommands.volume_up, MediaCommands.spin_this_in_new),
        num_minus.bind_numpad(MediaCommands.volume_down),
        num_asterisk.bind_numpad(MediaCommands.volume_mute),
        num_slash.bind_numpad(MediaCommands.volume_max),
    )
    return layout


from src.server.main import handler

with create_client(handler):
    keyboard.wait("esc")
