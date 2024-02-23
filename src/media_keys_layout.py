from typing import Callable

from commanding import ReceivedCommand, Command
from commands.commands import Code, cmd_show_status, cmd_hide_status
from hotkeys import Layout, Key, Hotkey
from hotkeys.numpad_hotkey import NumpadHotkey
from keys import *


def create_layout(sender: Callable[[ReceivedCommand], None]):

    layout = Layout("media", sender)

    stuffs = [num_0.bind_up_down(cmd_show_status, cmd_hide_status)]

    numdot = Hotkey(
        numdot_key,
        lambda e: None,
        lambda e: None,
    )

    def numpad_hotkey(key: str, cmd: Command, alt: Command | None = None):
        return NumpadHotkey(sender, Key(f"num {key}"), cmd).alt(alt)

    return (
        layout.add_numpad_hotkey(
            "-",
            volume_down,
        )
        .add_numpad_hotkey(
            "*",
            volume_mute,
        )
        .add_numpad_hotkey(
            "/",
            volume_max,
        )
        .add_numpad_hotkey(
            "1",
            seek_back,
        )
        .add_numpad_hotkey(
            "2",
            loop_track,
        )
        .add_numpad_hotkey(
            "3",
            seek_fwd,
        )
        .add_numpad_hotkey(
            "4",
            prev_track,
            prev_multi,
        )
        .add_numpad_hotkey(
            "5",
            play_pause,
        )
        .add_numpad_hotkey(
            "6",
            next_track,
            next_multi,
        )
        .add_numpad_hotkey(
            "7",
            undo,
        )
        .add_numpad_hotkey(
            "8",
            love,
        )
        .add_numpad_hotkey(
            "9",
            redo,
        )
        .add_numpad_hotkey(
            "enter",
            cancel,
            spin_this_in_last,
        )
        .add_numpad_hotkey(
            "+",
            volume_up,
            spin_this_in_new,
        )
    )
    return layout.add(
        num0,
        numdot,
        numpad_hotkey("-", "volume_down", "🔈"),
        numpad_hotkey("*", "volume_mute", "🔇"),
        numpad_hotkey("/", "volume_max", "🔊"),
        numpad_hotkey("1", "seek_back", "⬅️"),
        numpad_hotkey("2", "loop_track", "🔂"),
        numpad_hotkey("3", "seek_fwd", "➡️"),
        numpad_hotkey("4", "prev_track", "⏪").alt("prev_multi", "⏮️"),
        numpad_hotkey("5", "play_pause", "⏯️"),
        numpad_hotkey("6", "next_track", "⏩").alt("next_multi", "⏭️"),
        numpad_hotkey("7", "undo", "↩️"),
        numpad_hotkey("8", "love", "❤️"),
        numpad_hotkey("9", "redo", "↪️"),
        numpad_hotkey("enter", "cancel", "❌️").alt("spin_this_in_last", "🔄"),
        numpad_hotkey("+", "volume_up", "🔊").alt("spin_this_in_new", "🔄*"),
    )
