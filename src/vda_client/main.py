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
                caps: DesktopCommands.pan_to(1),
                caps + mouse1: DesktopCommands.drag_to(1),
                caps + mouse2: DesktopCommands.shove_to(1),
            }
        ),
        key_2.bind.whens(
            {
                caps: DesktopCommands.pan_to(2),
                caps + mouse1: DesktopCommands.drag_to(2),
                caps + mouse2: DesktopCommands.shove_to(2),
            }
        ),
        key_3.bind.whens(
            {
                caps: DesktopCommands.pan_to(3),
                caps + mouse1: DesktopCommands.drag_to(3),
                caps + mouse2: DesktopCommands.shove_to(3),
            }
        ),
        key_4.bind.whens(
            {
                caps: DesktopCommands.pan_to(4),
                caps + mouse1: DesktopCommands.drag_to(4),
                caps + mouse2: DesktopCommands.shove_to(4),
            }
        ),
        key_5.bind.whens(
            {
                caps: DesktopCommands.pan_to(5),
                caps + mouse1: DesktopCommands.drag_to(5),
                caps + mouse2: DesktopCommands.shove_to(5),
            }
        ),
        key_6.bind.whens(
            {
                caps: DesktopCommands.pan_to(6),
                caps + mouse1: DesktopCommands.drag_to(6),
                caps + mouse2: DesktopCommands.shove_to(6),
            }
        ),
        key_7.bind.whens(
            {
                caps: DesktopCommands.pan_to(7),
                caps + mouse1: DesktopCommands.drag_to(7),
                caps + mouse2: DesktopCommands.shove_to(7),
            }
        ),
        key_8.bind.whens(
            {
                caps: DesktopCommands.pan_to(8),
                caps + mouse1: DesktopCommands.drag_to(8),
                caps + mouse2: DesktopCommands.shove_to(8),
            }
        ),
        key_9.bind.whens(
            {
                caps: DesktopCommands.pan_to(9),
                caps + mouse1: DesktopCommands.drag_to(9),
                caps + mouse2: DesktopCommands.shove_to(9),
            }
        ),
        key_a.bind.whens(
            {
                caps: DesktopCommands.pan_left,
                caps + mouse1: DesktopCommands.drag_left,
                caps + mouse2: DesktopCommands.shove_left,
            }
        ),
        key_d.bind.whens(
            {
                caps: DesktopCommands.pan_right,
                caps + mouse1: DesktopCommands.drag_right,
                caps + mouse2: DesktopCommands.shove_right,
            }
        ),
    )
    return layout


logger.info("Starting up...")
create_client().__enter__()

while True:
    sleep(1)
