import tkinter as tk

from src.ui.make_clickthrough import make_clickthrough


class ToolTip(object):
    def __init__(self, widget):
        self.widget = widget
        self.tipwindow = None
        self.id = None
        self.x = self.y = 0

    def calculate_position(self):
        # Get the screen width and height
        screen_width = self.widget.winfo_screenwidth()
        screen_height = self.widget.winfo_screenheight()

        # Calculate position: 200px above the bottom and 200px from the right
        x = screen_width - 200
        y = screen_height - 200

        return x, y
    def show_tip(self, text):
        "Display text in tooltip window"
        self.text = text
        if self.tipwindow or not self.text:
            return
        self.tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_attributes('-topmost', 1)
        tw.wm_overrideredirect(True)
        tw.wm_geometry("+%d+%d" % self.calculate_position())
        label = tk.Label(tw, text=self.text, justify=tk.LEFT,
                         relief=tk.SOLID, borderwidth=1,
                         foreground="#000000",
                         font=("Segoe UI", "18", "normal"))
        label.pack(ipadx=1)

        tw.update_idletasks()  # Ensure window is created


    def hide_tip(self):
        tw = self.tipwindow
        self.tipwindow = None
        if tw:
            tw.destroy()

# Example usage
def create_tooltip(widget, text):
    tool_tip = ToolTip(widget)
    tool_tip.show_tip(text)

root = tk.Tk()
root.attributes('-topmost', 1, "-transparentcolor", "white")
root.wm_attributes("-topmost", True)
root.config(bg='white')
root.overrideredirect(True)
root.wm_geometry("+%d+%d" % (root.winfo_screenwidth() - 200, root.winfo_screenheight() - 200))
label = tk.Label(root, text="xd", justify=tk.LEFT,
                 background="#ffffff", relief=tk.SOLID, borderwidth= 0,
                 foreground="#000000", padx=1, pady=1,
                 font=("Segoe UI", "18", "normal"))
label.place_configure(x=0, y=0, height=200, width=200)
label2 = tk.Label(root, text="xasdsadsa", justify=tk.LEFT,

                    background="#ffffff", relief=tk.SOLID, borderwidth=0,
                    foreground="#000000",
                    font=("Segoe UI", "18", "normal"))
label2.place_configure(x=100, y=100, height=200, width=200)
label.pack(fill=tk.BOTH, expand=True)
label2.pack( fill=tk.BOTH, expand=True)
make_clickthrough(label)
make_clickthrough(label2)
root.mainloop()
