from typing import Protocol


from src.commanding.command_class import CommandClass
from src.commanding.commands import Command, command, parameterized_command


def number_to_emoji(number: int):
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


class DesktopCommands(metaclass=CommandClass, group_name="Desktop"):

    @command("🚫", "No Caps", False)
    def no_caps(self) -> None: ...

    @command("🫷📅", "Shove Left")
    def shove_left(self) -> None: ...

    @command("🫸📅", "Shove Right")
    def shove_right(self) -> None: ...

    @parameterized_command[int](lambda x: f"🫸📅{number_to_emoji(x)}", "Shove To {:d}")
    def shove_to(self, desktop_number: int) -> None: ...

    @parameterized_command[int](lambda x: f"📅🫱{number_to_emoji(x)}", "Drag To {:d}")
    def drag_to(self, desktop_number: int) -> None: ...

    @command("🫲📅", "Drag Left")
    def drag_left(self) -> None: ...

    @command("🫱📅", "Drag Right")
    def drag_right(self) -> None: ...

    @command("👁️⬅️", "Pan Right")
    def pan_right(self) -> None: ...

    @command("👁️➡️", "Pan Left")
    def pan_left(self) -> None: ...

    @parameterized_command[int](lambda d: f"👁️➡️{number_to_emoji(d)}", "Pan To {:d}")
    def pan_to(self, desktop_number: int) -> None: ...
