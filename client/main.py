import asyncio
import logging
from pathlib import Path
from typing import Awaitable
from venv import logger


from client.client_command_handler import ClientCommandHandler
from src.commanding.commands import Command
from src.commanding.handler import AsyncCommandHandler
from server.command_handler import MediaCommandHandler
from .keys import *
from src.spotify.now_playing import MediaStatus
from src.commands import *
from src.kb.layout import Layout
from .spotify_secret import spotify_creds
from src.setup_logging import setup_logging

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
        num_1.bind.default(MediaCommands.seek_bwd_small).when(
            num_0, MediaCommands.seek_bwd_big
        ),
        num_2.bind.default(MediaCommands.loop_track).when(
            num_0, MediaCommands.rewind_this
        ),
        num_3.bind.default(MediaCommands.seek_fwd_small).when(
            num_0, MediaCommands.seek_fwd_big
        ),
        num_4.bind.default(MediaCommands.prev_track).when(
            num_0, MediaCommands.prev_multi
        ),
        num_5.bind.default(MediaCommands.play_pause),
        num_6.bind.default(MediaCommands.next_track).when(
            num_0, MediaCommands.next_multi
        ),
        num_7.bind.default(MediaCommands.like_all).when(
            num_0, MediaCommands.transfer_to_current
        ),
        num_8.bind.default(MediaCommands.spin_this_in_last),
        num_plus.bind.default(MediaCommands.volume_up).when(
            num_dot, MediaCommands.spin_this_in_new
        ),
        num_9.bind.default(MediaCommands.transfer_to_phone),
        num_minus.bind.default(MediaCommands.volume_down).when(
            num_dot, MediaCommands.delete_current_playlist
        ),
        num_enter.bind.default(MediaCommands.cancel).when(
            num_dot, MediaCommands.spin_this_in_last
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
    spotify_creds,
    Path("./.store/history.state"),
)

create_client(handler).__enter__()
