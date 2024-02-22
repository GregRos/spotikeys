from threading import Thread
from time import sleep

from ui.floating_tooltip import FloatingTooltip

tt = FloatingTooltip()
tt.set_text("Title", "Body")
tt.show((-200, -200))
tt.start()
sleep(5)
tt.hide()
