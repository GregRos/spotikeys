from client.received_command import ReceivedCommand
from ui.now_playing import MediaStatus


class CommandDone:
    def __init__(self, command: ReceivedCommand, elapsed: float, state: MediaStatus):
        self.command = command
        self.elapsed = elapsed
        self.state = state

    @property
    def duration(self):
        return f"{self.elapsed * 1000:.0f}ms"


class CommandError:
    def __init__(
        self,
        command: ReceivedCommand,
        error: Exception,
        maybe_state: MediaStatus | None = None,
    ):
        self.command = command
        self.error = error
        self.maybe_state = maybe_state
