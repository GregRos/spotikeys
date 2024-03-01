from typing import Any, Literal, Tuple, Protocol

from keyboard import play

from src.commanding import Command
from src.commanding.commands import command, parameterized_command

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


class MediaCommands(Protocol):

    @parameterized_command("🔊")
    def volume_to(self, volume: int) -> None: ...

    @parameterized_command("🎚️")
    def seek_to(self, position: float) -> None: ...

    @parameterized_command("🔂")
    def repeat_to(self, repeat: Literal["track", "context", "off"]) -> None: ...

    @parameterized_command("🗑️")
    def delete_playlist(self, playlist_id: str) -> None: ...

    @parameterized_command("📝")
    def set_playlist_tracks(self, tracks: dict) -> None: ...

    @parameterized_command("⏮️")
    def skip_prev_n(self, n: int) -> None: ...

    @parameterized_command("⏭️")
    def skip_next_n(self, n: int) -> None: ...
    @command("▶️")
    def play(self) -> None: ...

    @command("⏸️")
    def pause(self) -> None: ...

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

    @command("❤️")
    def love(self) -> None: ...

    @parameterized_command("💔")
    def unlove(self, track_id: str) -> None: ...

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
