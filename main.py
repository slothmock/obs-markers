
import time
import threading
from app.logging import setup_logging
from app.core import MarkerApp
from app.gui.main_window import MarkerGUI
from app.hotkeys import Hotkeys


def main():
    logger = setup_logging(debug=True)

    app = MarkerApp(logger=logger)
    Hotkeys(app)

    def poll_loop():
        while True:
            app.poll()
            time.sleep(1)

    threading.Thread(target=poll_loop, daemon=True).start()

    gui = MarkerGUI(app)
    gui.run()


if __name__ == "__main__":
    main()