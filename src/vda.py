from threading import Thread
from typing import Any
import keyboard
from pyvda import AppView, VirtualDesktop, get_virtual_desktops

from src.kb.key import Key

number_of_active_desktops = len(get_virtual_desktops())
print(f"There are {number_of_active_desktops} active desktops")

current_desktop = VirtualDesktop.current()
print(f"Current desktop is number {current_desktop}")


def do_vda_change(e: Any):
    def do():
        print(
            f"Changing desktop from {VirtualDesktop.current().number} to {VirtualDesktop.current().number + 1}"
        )
        AppView.current().move(VirtualDesktop(VirtualDesktop.current().number + 1))

    Thread(target=do).start()


keyboard.wait("esc")
