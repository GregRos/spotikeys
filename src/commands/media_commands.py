from typing import Literal, Protocol, TypedDict


from src.commanding.commands import command, parameterized_command
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


class MediaCommands(Protocol):

    @command("📴")
    def exit(self) -> None: ...

    @parameterized_command("🔊")
    def volume_to(self, volume: int) -> None: ...

    @parameterized_command("🎚️")
    def seek_to(self, position: float) -> None: ...

    @parameterized_command("🔂")
    def repeat_to(self, repeat: Literal["track", "context", "off", False]) -> None: ...

    @parameterized_command("🗑️")
    def delete_playlist(self, playlist_id: str) -> None: ...

    @parameterized_command("📝")
    def set_playlist(self, tracks: SetPlaylistArgs) -> None: ...

    @parameterized_command("💔")
    def set_love_state(self, args: LoveStateArgs) -> None: ...

    @command("▶️")
    def play(self) -> None: ...

    @command("⏸️")
    def pause(self) -> None: ...

    @command("🔊")
    def volume_up(self) -> None: ...

    @command("🔈?")
    def get_volume(self) -> None: ...

    @command("🔈")
    def volume_down(self) -> None: ...

    @command("🔇")
    def volume_mute(self) -> None: ...

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

    @command("🔄")
    def spin_this_in_last(self) -> None: ...

    @command("🚮")
    def delete_current_playlist(self) -> None: ...

    @command("🎮")
    def transfer_to_current(self) -> None: ...

    @parameterized_command("🎮")
    def transfer_to_device(self, device: str | Device) -> None: ...
    @command("📱")
    def transfer_to_phone(self) -> None: ...

    @command("🔄*")
    def spin_this_in_new(self) -> None: ...

    @command("↩️")
    def undo(self) -> None: ...

    @command("↪️")
    def redo(self) -> None: ...

    @command("🔊 reset")
    def volume_reset(self) -> None: ...
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
