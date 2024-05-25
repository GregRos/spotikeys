import asyncio
import logging
from time import sleep

import keyboard

from src.kb.layout import Layout
from src.commands.desktop_commands import DesktopCommands
from src.vda_client.client import VdaClient
from .keys import (
    key_1,
    key_2,
    key_3,
    key_4,
    key_5,
    key_6,
    key_7,
    key_8,
    key_9,
    key_a,
    key_d,
    caps,
    mouse1,
    mouse2,
)

client_loop = asyncio.new_event_loop()

logger = logging.getLogger("vda_client")


def create_client():
    logger.info("Starting up...")
    cmd = VdaClient(client_loop)
    layout = Layout("media_keys", cmd)
    layout.add_bindings(
        key_1.bind.whens(
            {
                caps: DesktopCommands.move_to(1),
                caps + mouse1: DesktopCommands.fg_move_to_follow(1),
                caps + mouse2: DesktopCommands.fg_move_to(1),
            }
        ),
        key_2.bind.whens(
            {
                caps: DesktopCommands.move_to(2),
                caps + mouse1: DesktopCommands.fg_move_to_follow(2),
                caps + mouse2: DesktopCommands.fg_move_to(2),
            }
        ),
        key_3.bind.whens(
            {
                caps: DesktopCommands.move_to(3),
                caps + mouse1: DesktopCommands.fg_move_to_follow(3),
                caps + mouse2: DesktopCommands.fg_move_to(3),
            }
        ),
        key_4.bind.whens(
            {
                caps: DesktopCommands.move_to(4),
                caps + mouse1: DesktopCommands.fg_move_to_follow(4),
                caps + mouse2: DesktopCommands.fg_move_to(4),
            }
        ),
        key_5.bind.whens(
            {
                caps: DesktopCommands.move_to(5),
                caps + mouse1: DesktopCommands.fg_move_to_follow(5),
                caps + mouse2: DesktopCommands.fg_move_to(5),
            }
        ),
        key_6.bind.whens(
            {
                caps: DesktopCommands.move_to(6),
                caps + mouse1: DesktopCommands.fg_move_to_follow(6),
                caps + mouse2: DesktopCommands.fg_move_to(6),
            }
        ),
        key_7.bind.whens(
            {
                caps: DesktopCommands.move_to(7),
                caps + mouse1: DesktopCommands.fg_move_to_follow(7),
                caps + mouse2: DesktopCommands.fg_move_to(7),
            }
        ),
        key_8.bind.whens(
            {
                caps: DesktopCommands.move_to(8),
                caps + mouse1: DesktopCommands.fg_move_to_follow(8),
                caps + mouse2: DesktopCommands.fg_move_to(8),
            }
        ),
        key_9.bind.whens(
            {
                caps: DesktopCommands.move_to(9),
                caps + mouse1: DesktopCommands.fg_move_to_follow(9),
                caps + mouse2: DesktopCommands.fg_move_to(9),
            }
        ),
        key_a.bind.whens(
            {
                caps: DesktopCommands.move_prev,
                caps + mouse1: DesktopCommands.fg_move_prev_follow,
                caps + mouse2: DesktopCommands.fg_move_prev,
            }
        ),
        key_d.bind.whens(
            {
                caps: DesktopCommands.move_next,
                caps + mouse1: DesktopCommands.fg_move_next_follow,
                caps + mouse2: DesktopCommands.fg_move_next,
            }
        ),
    )
    return layout


logger.info("Starting up...")
create_client().__enter__()

while True:
    sleep(1)
