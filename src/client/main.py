import asyncio
import ctypes
from datetime import datetime
import logging
from pathlib import Path
from threading import Thread
from time import sleep
from turtle import setup
from typing import Callable
from venv import logger

from colorama import init
import keyboard

from src.client.client_command_handler import ClientCommandHandler
from src.client.hotkeys.hotkey import Hotkey
from src.commanding.handler import AsyncCommandHandler
from src.server.command_handler import MediaCommandHandler
from src.server.spotify.root import Root, SpotifyAuth
from .keys import *
from src.client.received_command import ReceivedCommand
from src.now_playing import MediaStatus
from src.commands import *
from src.client.hotkeys.layout import Layout

from src.log_config import setup_logging

setup_logging()

client_loop = asyncio.new_event_loop()


def create_client(send: AsyncCommandHandler[Command, MediaStatus]):
    logger = logging.getLogger("client")
    logger.info("Starting up...")
    cmd = ClientCommandHandler(client_loop, send)
    layout = Layout("media_keys", cmd)
    layout.add_bindings(
        num_dot.bind_off(),
        num_0.bind_up_down(MediaCommands.show_status, MediaCommands.hide_status),
        num_1.bind_numpad(MediaCommands.seek_bwd),
        num_2.bind_numpad(MediaCommands.loop_track, MediaCommands.rewind_this),
        num_3.bind_numpad(MediaCommands.seek_fwd),
        num_4.bind_numpad(MediaCommands.prev_track, MediaCommands.prev_multi),
        num_5.bind_numpad(MediaCommands.play_pause),
        num_6.bind_numpad(MediaCommands.next_track, MediaCommands.next_multi),
        num_7.bind_numpad(MediaCommands.undo, MediaCommands.transfer_to_current),
        num_8.bind_numpad(MediaCommands.love),
        num_9.bind_numpad(MediaCommands.redo, MediaCommands.transfer_to_phone),
        num_enter.bind_numpad(MediaCommands.cancel, MediaCommands.spin_this_in_last),
        num_plus.bind_numpad(MediaCommands.volume_up, MediaCommands.spin_this_in_new),
        num_minus.bind_numpad(
            MediaCommands.volume_down, MediaCommands.delete_current_playlist
        ),
        num_asterisk.bind_numpad(MediaCommands.volume_mute, MediaCommands.exit),
        num_slash.bind_numpad(MediaCommands.volume_reset),
    )
    return layout


def create_vda():
    layout = Layout("vda")


logger = logging.getLogger("server")
logger.info("Starting up...")
handler = MediaCommandHandler(
    {
        "client_id": "b996e2c82b574509bec24fbd11eda035",
        "client_secret": "2370df9b5a7840a183f44bbd795483fa",
        "redirect_uri": "http://localhost:12000",
    },
    Path("./history.state"),
)

create_client(handler).__enter__()
