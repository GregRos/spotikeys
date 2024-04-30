from dataclasses import dataclass
from tkinter import Tk
from typing import Tuple


@dataclass
class Geometry:
    height: int
    width: int
    x: int
    y: int

    def normalize(self, tk: Tk):
        pos_x, pos_y = self.x, self.y
        screen_width = tk.winfo_screenwidth()
        screen_height = tk.winfo_screenheight()
        if pos_x < 0:
            pos_x = screen_width + pos_x
        if pos_y < 0:
            pos_y = screen_height + pos_y
        return Geometry(height=self.height, width=self.width, x=pos_x, y=pos_y)

    def to_tk(self):
        return f"{self.width}x{self.height}+{self.x}+{self.y}"
