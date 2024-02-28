import time
import traceback
from typing import Callable


from src.client.received_command import ReceivedCommand
from src.client.ui.display_thread import ActivityDisplay
from src.client.ui.now_playing import MediaStatus
from src.commanding.commands import Command


class Commander:
    _thread: ActivityDisplay

    def __init__(self, send: Callable[[Command], MediaStatus | None]):
        self._send = send
        self._display = ActivityDisplay()

    def __call__(self, r_command: ReceivedCommand):
        def run_rcommand():
            self._display.run(lambda tt: tt.notify_command_start(r_command), False)
            start = time.time()
            try:
                result = self._send(r_command.command)
            except Exception as e:
                traceback.print_exc()
                x = e
                self._display.run(
                    lambda tt: tt.notify_command_errored(r_command.command, x)
                )
            else:
                elapsed = time.time() - start
                if not result:
                    print(f"Command {r_command.command} returned None")
                    raise ValueError(f"Command {r_command.command} returned None")
                self._display.run(
                    lambda tt: tt.notify_command_done(r_command, elapsed, result)
                )
