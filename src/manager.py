import keyboard

from commanding import CommandManager, Command, ReceivedCommand
from commands import *
from spotify.root import Root

command_spotify_manager = CommandManager[Code](cmd_cancel)

root = Root()


@command_spotify_manager.handles(cmd_seek_fwd)
def _on_seek_fwd(received: ReceivedCommand[Code]):
    root.player.progress += 30


@command_spotify_manager.handles(cmd_seek_back)
def _on_seek_back(received: ReceivedCommand[Code]):
    root.player.progress -= 30


@command_spotify_manager.handles(cmd_loop_track)
def _on_loop_track(received: ReceivedCommand[Code]):
    root.player.repeat = "track"
    root.player.progress = 0


@command_spotify_manager.handles(cmd_play_pause)
def _on_play_pause(received: ReceivedCommand[Code]):
    root.player.play_pause()


@command_spotify_manager.handles(cmd_prev_track)
def _on_prev_track(received: ReceivedCommand[Code]):
    root.player.prev_track()


@command_spotify_manager.handles(cmd_next_track)
def _on_next_track(received: ReceivedCommand[Code]):
    root.player.next_track()


@command_spotify_manager.handles(cmd_undo)
def _on_undo(received: ReceivedCommand[Code]):
    print(f"Received command: {received}")


@command_spotify_manager.handles(cmd_love)
def _on_love(received: ReceivedCommand[Code]):
    track = root.player.track
    track.save()
    track.album.save()
    track.artists[0].save()


@command_spotify_manager.handles(cmd_redo)
def _on_redo(received: ReceivedCommand[Code]):
    print(f"Received command: {received}")


@command_spotify_manager.handles(cmd_spin_this_in_last)
def _on_spin_this_in_last(received: ReceivedCommand[Code]):
    print(f"Received command: {received}")


@command_spotify_manager.handles(cmd_volume_up)
def _on_volume_up(received: ReceivedCommand[Code]):
    keyboard.send("volume up")


@command_spotify_manager.handles(cmd_volume_down)
def _on_volume_down(received: ReceivedCommand[Code]):
    keyboard.send("volume down")


@command_spotify_manager.handles(cmd_volume_mute)
def _on_volume_mute(received: ReceivedCommand[Code]):
    keyboard.send("volume mute")


@command_spotify_manager.handles(cmd_spin_this_in_new)
def _on_spin_this_in_new(received: ReceivedCommand[Code]):
    print(f"Received command: {received}")


@command_spotify_manager.handles(cmd_volume_max)
def _on_volume_max(received: ReceivedCommand[Code]):
    print(f"Received command: {received}")


@command_spotify_manager.handles(cmd_prev_multi)
def _on_prev_multi(received: ReceivedCommand[Code]):
    print(f"Received command: {received}")


@command_spotify_manager.handles(cmd_next_multi)
def _on_next_multi(received: ReceivedCommand[Code]):
    print(f"Received command: {received}")


@command_spotify_manager.handles(cmd_show_status)
def _on_show_status(received: ReceivedCommand[Code]):
    print(f"Received command: {received}")


@command_spotify_manager.handles(cmd_hide_status)
def _on_hide_status(received: ReceivedCommand[Code]):
    print(f"Received command: {received}")
