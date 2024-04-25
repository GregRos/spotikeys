import asyncio
import logging
from time import sleep

import keyboard

from src.client.hotkeys.layout import Layout
from src.commands.desktop_commands import DesktopCommands
from src.vda_client.client import VdaClient
from .keys import (
    win_1,
    win_2,
    win_3,
    win_4,
    win_5,
    win_6,
    win_7,
    win_8,
    win_9,
    win_a,
    win_d,
)

client_loop = asyncio.new_event_loop()

logger = logging.getLogger("vda_client")


def create_client():
    logger.info("Starting up...")
    cmd = VdaClient(client_loop)
    layout = Layout("media_keys", cmd)
    layout.add_bindings(
        win_1.bind(
            DesktopCommands.move_to(1),
            DesktopCommands.fg_move_to_follow(1),
            DesktopCommands.fg_move_to(1),
        ),
        win_2.bind(
            DesktopCommands.move_to(2),
            DesktopCommands.fg_move_to_follow(2),
            DesktopCommands.fg_move_to(2),
        ),
        win_3.bind(
            DesktopCommands.move_to(3),
            DesktopCommands.fg_move_to_follow(3),
            DesktopCommands.fg_move_to(3),
        ),
        win_4.bind(
            DesktopCommands.move_to(4),
            DesktopCommands.fg_move_to_follow(4),
            DesktopCommands.fg_move_to(4),
        ),
        win_5.bind(
            DesktopCommands.move_to(5),
            DesktopCommands.fg_move_to_follow(5),
            DesktopCommands.fg_move_to(5),
        ),
        win_6.bind(
            DesktopCommands.move_to(6),
            DesktopCommands.fg_move_to_follow(6),
            DesktopCommands.fg_move_to(6),
        ),
        win_7.bind(
            DesktopCommands.move_to(7),
            DesktopCommands.fg_move_to_follow(7),
            DesktopCommands.fg_move_to(7),
        ),
        win_8.bind(
            DesktopCommands.move_to(8),
            DesktopCommands.fg_move_to_follow(8),
            DesktopCommands.fg_move_to(8),
        ),
        win_9.bind(
            DesktopCommands.move_to(9),
            DesktopCommands.fg_move_to_follow(9),
            DesktopCommands.fg_move_to(9),
        ),
        win_a.bind(
            DesktopCommands.move_prev,
            DesktopCommands.fg_move_prev,
            DesktopCommands.fg_move_prev_follow,
        ),
        win_d.bind(
            DesktopCommands.move_next,
            DesktopCommands.fg_move_next,
            DesktopCommands.fg_move_next_follow,
        ),
    )
    return layout


logger.info("Starting up...")
create_client().__enter__()

while True:
    sleep(1)
