from src.commanding import Command
from src.commands import Code


class BusyError(Exception):
    def __init__(self, command: Command):
        super().__init__(f"Command {command} is still being handled.")
        self.command = command


class NoHandlerError(Exception):
    def __init__(self, command: Command):
        super().__init__(f"No handler for {command}")
        self.command = command


class LocalCommandError(Exception):
    def __init__(self, command: Command):
        super().__init__(
            f"Command {command} is local and cannot be handled by the server"
        )
        self.command = command
