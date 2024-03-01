from io import FileIO
from os import PathLike
from typing import BinaryIO

from src.commanding import Command

unknown_command = Command("unknown", "❓")


class PersistentCommandHistory:
    file: BinaryIO

    def __init__(self, filename: PathLike, commands: object):
        self.filename = filename
        self.is_disabled = False
        self.file = self.file = open(self.filename, "ab+", buffering=0)

        self.commands = {
            k: v for k, v in commands.__dict__.items() if isinstance(v, Command)
        }

    def close(self):
        self.file.close()

    def _parse(self, line: str):
        return self.commands[line.strip()]

    def pop(self):
        lines = self.file.readlines()
        if not lines:
            return None
        last_line = lines[-1]
        pop_length = len(last_line)
        if not last_line.strip():
            last_line = lines[-2]
            pop_length += len(last_line) + 1
        if last_line == "unknown":
            raise ValueError("Cannot undo unknown command!")
        self.file.seek(-pop_length, 2)
        self.file.truncate()
        if not last_line.strip():
            return self.pop()
        code = last_line.decode(encoding="utf-8")
        return self._parse(code)

    def not_undoable(self):
        self.push(unknown_command)

    def push(self, command: Command):
        self.file.write(command.code.encode(encoding="utf-8"))
        self.file.write(b"\n")

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
