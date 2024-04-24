from src.commanding import Command
from src.server.history.command_history import PersistentCommandHistory


class UndoWaiter:
    def __init__(self, history: PersistentCommandHistory, command: Command):
        self._command = command
        self._history = history

    def __enter__(self):
        pass

    def __exit__(self, *args):
        if len(args) == 0:
            self._history.push(self._command)
