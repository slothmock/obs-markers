import threading
import time
from app.core import MarkerApp
from app.gui.main_window import MarkerGUI
from app.logging import setup_logging

def main():
    logger = setup_logging(debug=True)
    app = None

    try:
        app = MarkerApp(logger=logger)

        # Start OBS polling in background thread
        def poll_loop():
            while True:
                app.poll()
                time.sleep(1)

        threading.Thread(target=poll_loop, daemon=True).start()

        # Start GUI (blocking)
        gui = MarkerGUI(app)
        gui.run()

    except KeyboardInterrupt:
        logger.info("Shutting down via KeyboardInterrupt.")

    except Exception as e:
        logger.exception(f"Fatal error in main: {e}")

    finally:
        if app is not None:
            app.config.save()
            logger.info("Config saved. Shutting down.")

if __name__ == "__main__":
    main()
