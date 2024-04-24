from typing import Protocol

from src.commanding.commands import command, parameterized_command


class DesktopCommands(Protocol):

    @command("📅👈⏹️")
    def fg_move_prev(self) -> None: ...

    @command("⏹️👉📅")
    def fg_move_next(self) -> None: ...

    @command("📅👈")
    def fg_move_prev_follow(self) -> None: ...

    @command("👉📅")
    def fg_move_next_follow(self) -> None: ...

    @command("▶️▶️")
    def move_next(self) -> None: ...

    @command("◀️◀️")
    def move_prev(self) -> None: ...

    @parameterized_command("")
    def move_to(self, desktop_number: int) -> None: ...
