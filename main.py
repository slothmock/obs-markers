
import time
import threading
from app.logging import setup_logging
from app.core import MarkerApp
from app.gui.main_window import MarkerGUI


def main():
    try:
        logger = setup_logging(debug=True)

        app = MarkerApp(logger=logger)

        def poll_loop():
            while True:
                app.poll()
                time.sleep(1)

        threading.Thread(target=poll_loop, daemon=True).start()

        gui = MarkerGUI(app)
        gui.run()
    except KeyboardInterrupt:
        logger.info(f"Shutting down via KeyboardInterrupt")
        exit(0)

if __name__ == "__main__":
    main()