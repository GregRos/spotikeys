from io import FileIO
from os import PathLike
from typing import BinaryIO

from commanding import Command


class PersistentCommandHistory:
    file: BinaryIO

    def __init__(self, filename: PathLike, commands: object):
        self.filename = filename
        self.commands = commands

    def __enter__(self):
        self.file = open(self.filename, "ab+", buffering=0)
        return self

    def __exit__(self, *args):
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

        self.file.seek(-pop_length, 2)
        self.file.truncate()
        if not last_line.strip():
            return self.pop()
        code = last_line.decode(encoding="utf-8")
        return self._parse(code)

    def push(self, command: Command):
        self.file.write(command.code.encode(encoding="utf-8"))
        self.file.write(b"\n")
