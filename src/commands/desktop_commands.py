from typing import Protocol


from src.commanding.commands import command, parameterized_command


def number_to_emoji(number):
    emoji_digits = {
        "0": "0️⃣",
        "1": "1️⃣",
        "2": "2️⃣",
        "3": "3️⃣",
        "4": "4️⃣",
        "5": "5️⃣",
        "6": "6️⃣",
        "7": "7️⃣",
        "8": "8️⃣",
        "9": "9️⃣",
    }

    emoji_number = ""
    for digit in str(number):
        if digit in emoji_digits:
            emoji_number += emoji_digits[digit]
        else:
            emoji_number += digit

    return emoji_number


class DesktopCommands(Protocol):

    @command("📅👈⏹️")
    def fg_move_prev(self) -> None: ...

    @command("⏹️👉📅")
    def fg_move_next(self) -> None: ...

    @parameterized_command(lambda x: f"📅👉{number_to_emoji(x)}")
    def fg_move_to(self, desktop_number: int) -> None: ...

    @parameterized_command(lambda x: f"👉📅{number_to_emoji(x)}")
    def fg_move_to_follow(self, desktop_number: int) -> None: ...

    @command("📅👈")
    def fg_move_prev_follow(self) -> None: ...

    @command("👉📅")
    def fg_move_next_follow(self) -> None: ...

    @command("▶️▶️")
    def move_next(self) -> None: ...

    @command("◀️◀️")
    def move_prev(self) -> None: ...

    @parameterized_command(number_to_emoji)
    def move_to(self, desktop_number: int) -> None: ...
