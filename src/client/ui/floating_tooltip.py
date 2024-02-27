from tkinter import Tk, Label, SOLID, LEFT, CENTER
from typing import Tuple

from src.client.received_command import ReceivedCommand
from .make_clickthrough import make_clickthrough
from src.client.ui.events import CommandDone, CommandError
from src.client.ui.now_playing import MediaStatus


def format_duration(seconds):
    minutes, seconds = divmod(seconds, 60)
    return f"{minutes:02d}:{seconds:02d}"


class MediaTooltip:
    _tk: Tk
    _pos: Tuple[int, int]

    def __init__(self, tk: Tk):
        self._tk = tk
        self._pos = (-250, -250)
        tk.attributes("-topmost", 1, "-transparentcolor", "black")
        tk.wm_attributes("-topmost", True)
        tk.config(bg="black")
        tk.overrideredirect(True)
        self._command_line = title = Label(
            tk,
            text="xd",
            justify=CENTER,
            relief=SOLID,
            borderwidth=0,
            background="#000000",
            foreground="#ffffff",
            font=("Segoe UI Emoji", 18, "bold"),
        )

        self._song_title_line = Label(
            tk,
            text="xd",
            justify=CENTER,
            relief=SOLID,
            borderwidth=0,
            background="#000000",
            foreground="#ffffff",
            font=("Segoe UI Emoji", 12),
        )

        self._song_artist_line = Label(
            tk,
            text="xd",
            justify=CENTER,
            relief=SOLID,
            borderwidth=0,
            background="#000000",
            foreground="#ff0000",
            font=("Segoe UI Emoji", 12),
        )

        self._song_progress_line = Label(
            tk,
            text="xd",
            justify=CENTER,
            relief=SOLID,
            borderwidth=0,
            background="#000000",
            foreground="#ff0000",
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

    def _set_command_header(self, text: str):
        command_line = self._command_line
        command_line.config(text=text)
        command_line.place(x=0, y=0, width=200)
        command_line.pack(ipadx=15, fill="x", expand=True)
        make_clickthrough(command_line)

    def _set_first_line(self, line: str):
        self._song_title_line.config(text=line)
        self._song_title_line.place(x=0, y=50, width=200)
        self._song_title_line.pack(ipadx=15, fill="x", expand=True)
        make_clickthrough(self._song_title_line)

    def _set_artist_line(self, line: str):
        self._song_artist_line.config(text=line)
        self._song_artist_line.place(x=0, y=100, width=200)
        self._song_artist_line.pack(ipadx=15, fill="x", expand=True)
        make_clickthrough(self._song_artist_line)

    def _set_progress_line(self, line: str):
        self._song_progress_line.config(text=line)
        self._song_progress_line.place(x=0, y=150, width=200)
        self._song_progress_line.pack(ipadx=15, fill="x", expand=True)
        make_clickthrough(self._song_progress_line)

    def _place_window(self):
        self._tk.wm_geometry("+%d+%d" % self._pos)
        self._tk.update_idletasks()

    def notify_command_errored(self, errored: CommandError):
        self._set_command_header(errored.command.command.__str__())
        self._set_first_line(f"{errored.error}")
        for label in (self._song_artist_line, self._song_progress_line):
            label.pack_forget()
        self._place_window()

    def notify_command_start(self, command: ReceivedCommand):
        self._set_command_header(command.__str__())
        self._set_first_line("⋯ sent ⋯")
        for label in (self._song_artist_line, self._song_progress_line):
            label.pack_forget()
        self._place_window()

    def notify_command_done(
        self, finished: ReceivedCommand, duration: float, state: MediaStatus
    ):
        text = f"{finished.command.label} {duration}"
        self._set_command_header(text)
        self._show_media(state)

    def show_progress(self, status: MediaStatus):
        self._command_line.pack_forget()
        self._show_media(status)

    def _show_media(self, status: MediaStatus):
        artist_line = " ● ".join([status.artist, status.album])
        remaining_time = format_duration(status.duration - status.position)
        full_blocks = int(status.percent / 10)
        progress_line = (
            f"{'█' * full_blocks}{'░' * (10 - full_blocks)} {remaining_time}"
        )
        self._set_first_line(status.title)
        self._set_artist_line(artist_line)
        self._set_progress_line(progress_line)
        self._place_window()

    def hide(self):
        self._tk.withdraw()
        self._tk.update_idletasks()
