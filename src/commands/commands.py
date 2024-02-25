from typing import Any, Literal, Tuple, Protocol

from commanding import Command, CommandSet
from commanding.commands import command
from src.server.errors import NoHandlerError

Code = Literal[
    "show_status",
    "hide_status",
    "next_track",
    "prev_track",
    "play_pause",
    "loop_track",
    "seek_fwd",
    "seek_back",
    "rewind_context",
    "repeat_track",
    "love",
    "spin_this_in_last",
    "spin_this_in_new",
    "volume_up",
    "volume_down",
    "volume_max",
    "volume_mute",
    "redo",
    "undo",
    "cancel",
    "rewind_this",
    "next_multi",
    "prev_multi",
]

commands = CommandSet()


class MediaCommands(Protocol):
    @command("🔊")
    def volume_up(self) -> None: ...

    @command("🔈")
    def volume_down(self) -> None: ...

    @command("🔇")
    def volume_mute(self) -> None: ...

    @command("🔊")
    def volume_max(self) -> None: ...

    @command("⬅️")
    def seek_bwd(self) -> None: ...

    @command("🔂")
    def loop_track(self) -> None: ...

    @command("➡️")
    def seek_fwd(self) -> None: ...

    @command("⏪")
    def prev_track(self) -> None: ...

    @command("⏯️")
    def play_pause(self) -> None: ...

    @command("⏩")
    def next_track(self) -> None: ...

    @command("🔂")
    def repeat_track(self) -> None: ...

    @command("❤️")
    def love(self) -> None: ...

    @command("🔄")
    def spin_this_in_last(self) -> None: ...

    @command("🔄*")
    def spin_this_in_new(self) -> None: ...

    @command("↩️")
    def undo(self) -> None: ...

    @command("↪️")
    def redo(self) -> None: ...

    @command("❌️")
    def cancel(self) -> None: ...

    @command("🔄")
    def rewind_this(self) -> None: ...

    @command("⏭️")
    def next_multi(self) -> None: ...

    @command("⏮️")
    def prev_multi(self) -> None: ...

    @command("📊")
    def show_status(self) -> None: ...

    @command("📊")
    def get_status(self) -> None: ...

    @command("📊")
    def hide_status(self) -> None: ...





cmd_volume_down = commands.define("volume_down", "🔈")
cmd_volume_mute = commands.define("volume_mute", "🔇")
cmd_volume_up = commands.define("volume_up", "🔊")
cmd_volume_max = commands.define("volume_max", "🔊")
cmd_seek_bwd = commands.define("seek_back", "⬅️")
cmd_loop_track = commands.define("loop_track", "🔂")
cmd_seek_fwd = commands.define("seek_fwd", "➡️")
cmd_prev_track = commands.define("prev_track", "⏪")
cmd_play_pause = commands.define("play_pause", "⏯️")
cmd_next_track = commands.define("next_track", "⏩")
cmd_undo = commands.define("undo", "↩️")
cmd_love = commands.define("love", "❤️")
cmd_redo = commands.define("redo", "↪️")
cmd_cancel = commands.define("cancel", "❌️")
cmd_spin_this_in_last = commands.define("spin_this_in_last", "🔄")

cmd_spin_this_in_new = commands.define("spin_this_in_new", "🔄*")
cmd_prev_multi = commands.define("prev_multi", "⏮️")
cmd_next_multi = commands.define("next_multi", "⏭️")

cmd_show_status = commands.define("show_status", "📊")
cmd_get_status = commands.define("get_status", "📊")
cmd_hide_status = commands.define("hide_status", "📊")
