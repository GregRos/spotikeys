from typing import Literal, Protocol, TypedDict


from src.commanding.command_class import CommandClass
from src.commanding.commands import Command, command, parameterized_command
from src.spotify.device import Device


class LoveStateArgs(TypedDict):
    id: str
    track_love: bool
    album_love: bool
    artist_love: bool


class SetPlaylistArgs(TypedDict):
    id: str
    name: str
    tracks: list[str]
    description: str


RepeatMode = Literal["track", "context", "off", False]


class MediaCommands(metaclass=CommandClass, group_name="Media"):

    @command("📴", "Bye!")
    def exit(self) -> None: ...

    @parameterized_command("🔊", "Vol To")
    def volume_to(self, volume: int) -> None: ...

    @parameterized_command[int]("🎚️", lambda x: f"Seek {f'+{x}' if x > 0 else x}")
    def seek_to(self, position: float) -> None: ...

    @parameterized_command[RepeatMode]("🔂", "Set Repeat {}")
    def repeat_to(self, repeat: RepeatMode) -> None: ...

    @parameterized_command[str]("🗑️", "Del {}")
    def delete_playlist(self, playlist_id: str) -> None: ...

    @parameterized_command[SetPlaylistArgs]("📝", "Set %O")
    def set_playlist(self, tracks: SetPlaylistArgs) -> None: ...

    @parameterized_command[LoveStateArgs]("💔", lambda x: f"Love ...")
    def set_love_state(self, args: LoveStateArgs) -> None: ...

    @command("▶️", "Play")
    def play(self) -> None: ...

    @command("⏸️", "Pause")
    def pause(self) -> None: ...

    @command("🔊➕", "Vol+ Local")
    def volume_up(self) -> None: ...

    @command("🔈?", "Get Vol Local")
    def get_volume(self) -> None: ...

    @command("🔈➖", "Vol- Local")
    def volume_down(self) -> None: ...

    @command("🔇", "Mute Local")
    def volume_mute(self) -> None: ...

    @command("⬅️", "Seek -10s")
    def seek_bwd_small(self) -> None: ...

    @command("🔂", "Loop Track")
    def loop_track(self) -> None: ...

    @command("➡️", "Seek +10s")
    def seek_fwd_small(self) -> None: ...

    @command("➡️➡️", "Seek +30s")
    def seek_fwd_big(self) -> None: ...

    @command("⬅️⬅️", "Seek -30s")
    def seek_bwd_big(self) -> None: ...

    @command("⏪", "Prev Track")
    def prev_track(self) -> None: ...

    @command("⏯️", "Play/Pause")
    def play_pause(self) -> None: ...

    @command("⏩", "Next Track")
    def next_track(self) -> None: ...

    @command("❤️", "Love Track")
    def like_track(self) -> None: ...

    @command("💞", "Follow")
    def like_all(self) -> None: ...

    @command("💔", "Unlove")
    def unlike(self) -> None: ...

    @command("♻️", "Spin in Last PL")
    def spin_this_in_last(self) -> None: ...

    @command("🚮", "Delete PL")
    def delete_current_playlist(self) -> None: ...

    @command("🎮", "Play to Local")
    def transfer_to_current(self) -> None: ...

    @parameterized_command[str]("🎮", "Play to {}")
    def transfer_to_device(self, device: str | Device) -> None: ...

    @command("📱", "Play to Phone")
    def transfer_to_phone(self) -> None: ...

    @command("🔄", "Spin in New PL")
    def spin_this_in_new(self) -> None: ...

    @command("↩️", "Undo")
    def undo(self) -> None: ...

    @command("↪️", "Redo")
    def redo(self) -> None: ...

    @command("🔊🎚️", "Vol Reset")
    def volume_reset(self) -> None: ...

    @command("❌️", "Cancel")
    def cancel(self) -> None: ...

    @command("🔄", "Rewind")
    def rewind_this(self) -> None: ...

    @command("⏭️", "Next ++Track")
    def next_multi(self) -> None: ...

    @command("⏮️", "Prev ++Track")
    def prev_multi(self) -> None: ...

    @command("📊", "Show Status")
    def show_status(self) -> None: ...

    @command("📊", "Get Status")
    def get_status(self) -> None: ...

    @command("📊", "Hide Status")
    def hide_status(self) -> None: ...
