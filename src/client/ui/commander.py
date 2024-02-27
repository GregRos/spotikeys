import time
import traceback
from typing import Callable


from src.client.received_command import ReceivedCommand
from src.client.ui.display_thread import ActivityDisplay
from src.client.ui.now_playing import MediaStatus
from src.commanding.commands import Command


class Commander:

    def __init__(self, send: Callable[[Command], MediaStatus]):
        self._send = send
        self._display = ActivityDisplay()

    def __call__(self, r_command: ReceivedCommand):
        try:
            self._display.run(lambda tt: tt.notify_command_start(r_command), False)
            start = time.time()
            result = self._send(r_command.command)
            elapsed = time.time() - start
            self._display.run(
                lambda tt: tt.notify_command_done(r_command, elapsed, result)
            )

        except Exception as e:
            traceback.print_exc()
