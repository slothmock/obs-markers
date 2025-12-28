import time
import threading
from app.core import MarkerApp
from app.gui import MarkerGUI
from app.hotkeys import Hotkeys


app = MarkerApp()
Hotkeys(app)

def poll_loop():
    while True:
        app.poll()
        time.sleep(1)

threading.Thread(target=poll_loop, daemon=True).start()

gui = MarkerGUI(app)
gui.run()
