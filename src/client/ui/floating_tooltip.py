import ctypes
from math import trunc
from tkinter import Tk, Label, SOLID, LEFT, CENTER
from typing import Tuple


from src.client.kb.triggered_command import TriggeredCommand
from src.client.volume import VolumeInfo
from src.commanding.commands import Command
from .make_clickthrough import make_clickthrough
from src.now_playing import MediaStatus

ctypes.windll.shcore.SetProcessDpiAwareness(1)


def format_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{int(minutes):02d}:{int(seconds):02d}"


def truncate_text(text: str, max_length: int) -> str:
    if len(text) > max_length:
        return text[: max_length - 1] + "⋯"
    return text


class MediaTooltip:
    _tk: Tk
    _pos: Tuple[int, int]
    _status: MediaStatus
    _error = False

    def __init__(self, tk: Tk):
        self._tk = tk
        self._pos = (-450, -350)
        tk.attributes("-topmost", 1, "-transparentcolor", "black")
        tk.wm_attributes("-topmost", True)
        tk.config(bg="black")
        tk.overrideredirect(True)
        self._command_line = command_line = Label(
            tk,
            text=" ",
            justify=CENTER,
            relief=SOLID,
            borderwidth=0,
            background="#000000",
            foreground="#dddddd",
            font=("Segoe UI Emoji", 12, "normal"),
        )

        self._song_title_line = song_title_line = Label(
            tk,
            text=" ",
            justify=CENTER,
            relief=SOLID,
            borderwidth=0,
            background="#000000",
            foreground="#ffffff",
            font=("Segoe UI Emoji", 18),
        )

        self._song_artist_line = song_artist_line = Label(
            tk,
            text=" ",
            justify=CENTER,
            relief=SOLID,
            borderwidth=0,
            background="#000000",
            foreground="#aaaafb",
            font=("Segoe UI Emoji", 14),
        )

        self._song_progress_line = progress_line = Label(
            tk,
            text=" ",
            justify=LEFT,
            relief=SOLID,
            borderwidth=0,
            background="#000000",
            foreground="#ff0000",
            font=("Segoe UI Emoji", 15),
        )

        self._song_album_line = Label(
            tk,
            text=" ",
            justify=CENTER,
            relief=SOLID,
            borderwidth=0,
            background="#000000",
            foreground="#ff0000",
            font=("Segoe UI Emoji", 12),
        )

        self._volume_line = Label(
            tk,
            text=" ",
            justify=CENTER,
            relief=SOLID,
            borderwidth=0,
            background="#111111",
            foreground="#00ff00",
            font=("Segoe UI Emoji", 12),
        )

        self._tk.update_idletasks()

    def _normalize_pos(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        pos_x, pos_y = pos
        screen_width = self._tk.winfo_screenwidth()
        screen_height = self._tk.winfo_screenheight()
        if pos_x < 0:
            pos_x = screen_width + pos_x
        if pos_y < 0:
            pos_y = screen_height + pos_y
        return pos_x, pos_y

    def _set_album_line(self, line: str):
        pass

    _command_part_placed = False

    def _set_command_part(
        self, text: str, duration: str, bg: str = "#000000", place=True, font_size=12
    ):
        typeset = f"{text.ljust(30)}{str(duration)}"
        command_line = self._command_line
        command_line.config(
            text=typeset, background=bg, font=("Segoe UI Emoji", font_size)
        )
        # either place is true or the command line is not placed:
        if place or not self._command_part_placed:
            self._command_part_placed = True
            command_line.place(relx=0, rely=0, width=100)
            command_line.pack(ipadx=20, fill="both", ipady=5, expand=True)
            make_clickthrough(command_line)

    def _set_first_line(self, line: str, font_size=18):
        song_title_line = self._song_title_line
        song_title_line.config(
            text=truncate_text(line, 20), font=("Segoe UI Emoji", font_size)
        )
        song_title_line.place(x=0, y=20, width=200)
        song_title_line.pack(ipadx=15, fill="both", expand=True)
        make_clickthrough(song_title_line)

    def _set_volume_line(self, line: str):
        volume_line = self._volume_line
        volume_line.config(text=line)
        volume_line.place(x=0, y=200, width=20)
        volume_line.pack(ipadx=40, fill="both", ipady=15, expand=True)
        make_clickthrough(volume_line)

    def _set_artist_line(self, line: str):
        song_artist_line = self._song_artist_line
        song_artist_line.config(text=truncate_text(line, 20))
        song_artist_line.place(x=0, y=50, width=200)
        song_artist_line.pack(ipadx=15, fill="x", expand=True)
        make_clickthrough(self._song_artist_line)

    def _set_progress_line(self, line: str):
        progress_line = self._song_progress_line
        progress_line.config(text=line)
        progress_line.place(x=0, y=100, width=200)
        progress_line.pack(ipadx=20, fill="both", ipady=15, expand=True)
        make_clickthrough(progress_line)

    def show(self):
        self._place_window()

    def _place_window(self):
        self._tk.wm_geometry("420x250+%d+%d" % self._normalize_pos(self._pos))
        self._tk.deiconify()
        self._tk.update_idletasks()

    def notify_command_errored(self, command: Command, error: str, fate_emoji: str):
        self._error = True
        self._tk.attributes("-alpha", 1)
        self._set_command_part(f"{fate_emoji} {command.code}", "", "darkred", False, 18)
        self._set_first_line(error, 15)
        for label in (self._song_artist_line, self._song_progress_line):
            label.pack_forget()
        self._place_window()

    def notify_command_start(self, command: TriggeredCommand):
        if self._error:
            self._error = False
            self._command_line.pack_forget()
            self._set_first_line(" ")
        self._set_command_part("⌛ " + str(command), "⌛⌛", "darkblue", False)
        self._place_window()
        self._tk.attributes("-alpha", 0.85)
        self._tk.update_idletasks()

    def notify_show_status(self, status: MediaStatus | None = None):
        self._tk.attributes("-alpha", 1)

        self._set_command_part("status", "💡", "grey", False)
        if status:
            self._status = status
            self._show_media(status)
        self._place_window()
        self._tk.update_idletasks()

    def notify_command_done(
        self, finished: TriggeredCommand, duration: float, state: MediaStatus
    ):
        self._tk.attributes("-alpha", 1)
        self._status = state
        self._set_command_part(
            "✅ " + str(finished), f"{duration * 1000:.0f}ms", "green"
        )
        self._show_media(state)
        self._place_window()
        self._tk.update_idletasks()

    def show_progress(self, status: MediaStatus):
        self._command_line.pack_forget()
        self._show_media(status)

    def get_volume_line(self, info: VolumeInfo):
        empty = "◇"
        full = "◇" if info.mute else "◆"
        if info.mute:
            return f"🔇 {empty * 16}"
        full_boxes = trunc(info.volume / 100 * 16)
        return f"🔊 {full * full_boxes}{empty * (16 - full_boxes)}"

    def notify_volume_changed(self, info: VolumeInfo):
        volume_line = self.get_volume_line(info)
        self._set_volume_line(volume_line)
        self._place_window()
        self._tk.update_idletasks()

    def _show_media(self, status: MediaStatus):

        remaining_time = format_duration(status.duration - status.position)
        full_blocks = round(float(status.progress / 100) * 9)
        progress_line = f"{ '▶' if status.is_playing else '⏸' } {'█' * full_blocks}{'░' * (9 - full_blocks)} {remaining_time}"
        volume_line = self.get_volume_line(status.volume)
        self._set_first_line(status.title)
        self._set_artist_line(status.artist)
        self._set_progress_line(progress_line)
        self._set_album_line(status.album)
        self._set_volume_line(volume_line)
        self._place_window()

    def hide(self):
        self._tk.withdraw()
        self._tk.update_idletasks()
