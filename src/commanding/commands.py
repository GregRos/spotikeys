from __future__ import annotations


class Command[Code: str]:
    code: Code

    def __init__(self, command: Code, label: str, is_local: bool = False):
        self.code = command
        self.label = label
        self.is_local = is_local

    def local(self, is_local: bool = True):
        return Command[Code](self.code, self.label, is_local)

    def is_command(self, command: Command[Code]):
        return self.code == command.code

    def __str__(self):
        return f"{self.label} ({self.code})"
