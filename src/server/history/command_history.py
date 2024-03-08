from io import FileIO
from operator import is_
from os import PathLike, sep
from pathlib import Path
from typing import BinaryIO

from src.commanding import Command


def unknown_command(describe: str):
    return Command("unknown", describe)


expected_version = 1


class PersistentCommandHistory:
    file: BinaryIO

    def __init__(self, filename: PathLike, commands: object):
        self.filename = filename = Path(filename)
        self.is_disabled = False

    def close(self):
        self.file.close()

    def not_undoable(self, message: str):
        self.push(unknown_command(message))

    def push(self, command: Command):
        pass

    def no_tracking(self):
        return StopTrackingToken(self)


class StopTrackingToken:
    def __init__(self, parent: PersistentCommandHistory) -> None:
        self.parent = parent
        self._prev_state = parent.is_disabled

    def __enter__(self):
        self._prev_state = self.parent.is_disabled
        self.parent.is_disabled = True

    def __exit__(self, *args):
        self.parent.is_disabled = self._prev_state
