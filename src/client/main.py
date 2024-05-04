import asyncio
import logging
from pathlib import Path
from typing import Awaitable
from venv import logger


from src.client.client_command_handler import ClientCommandHandler
from src.commanding.commands import Command
from src.commanding.handler import AsyncCommandHandler
from src.server.command_handler import MediaCommandHandler
from .keys import *
from src.now_playing import MediaStatus
from src.commands import *
from src.client.hotkeys.layout import Layout

from src.log_config import setup_logging

setup_logging()

client_loop = asyncio.new_event_loop()


def create_client(send: AsyncCommandHandler[Command, Awaitable[MediaStatus]]):
    logger = logging.getLogger("client")
    logger.info("Starting up...")
    cmd = ClientCommandHandler(client_loop, send)
    layout = Layout("media_keys", cmd)
    layout.add_bindings(
        num_dot.bind.when(num_0, MediaCommands.show_status),
        num_0.bind.default(MediaCommands.show_status, MediaCommands.hide_status),
        num_1.bind.default(MediaCommands.seek_bwd),
        num_2.bind.default(MediaCommands.loop_track).when(
            num_0, MediaCommands.rewind_this
        ),
        num_3.bind.default(MediaCommands.seek_fwd),
        num_4.bind.default(MediaCommands.prev_track).when(
            num_0, MediaCommands.prev_multi
        ),
        num_5.bind.default(MediaCommands.play_pause),
        num_6.bind.default(MediaCommands.next_track).when(
            num_0, MediaCommands.next_multi
        ),
        num_7.bind.default(MediaCommands.love).when(
            num_0, MediaCommands.transfer_to_current
        ),
        num_8.bind.default(MediaCommands.spin_this_in_last),
        num_plus.bind.default(MediaCommands.volume_up).when(
            num_0, MediaCommands.spin_this_in_new
        ),
        num_9.bind.default(MediaCommands.delete_current_playlist).when(
            num_0, MediaCommands.transfer_to_phone
        ),
        num_minus.bind.default(MediaCommands.volume_down).when(
            num_0, MediaCommands.delete_current_playlist
        ),
        num_enter.bind.default(MediaCommands.cancel).when(
            num_0, MediaCommands.spin_this_in_last
        ),
        num_asterisk.bind.default(MediaCommands.volume_mute).when(
            num_0, MediaCommands.exit
        ),
        num_slash.bind.default(MediaCommands.volume_reset),
    )
    return layout


logger = logging.getLogger("server")
logger.info("Starting up...")
handler = MediaCommandHandler(
    {
        "client_id": "b996e2c82b574509bec24fbd11eda035",
        # This client secret is obsolete.
        "client_secret": "2370df9b5a7840a183f44bbd795483fa",
        "redirect_uri": "http://localhost:12000",
    },
    Path("./history.state"),
)

create_client(handler).__enter__()
