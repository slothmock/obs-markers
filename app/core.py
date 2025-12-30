import sys, time, logging

import obsws_python as obs
from app.markers import MarkerFileManager
from app.config import load_config, save_config


class MarkerApp:
    def __init__(self):
        # Config
        self.config = load_config()
        self.logger = logging.getLogger("OBSMarkers")

        self.logger.info("OBS Markers initializing")

        try:
            self.req_client = obs.ReqClient(host='localhost', port=4455)
            self.logger.debug("OBS ReqClient created")
        except Exception as e:
            self.logger.critical(
                "Failed to create OBS request client",
                exc_info=e
            )
            sys.exit(1)

        try:
            stats = self.req_client.get_stats()
            self.logger.info(
                "OBS connected | CPU %.2f%% | Memory %.2f MB",
                stats.cpu_usage,
                stats.memory_usage
            )
        except Exception as e:
            self.logger.critical(
                "OBS did not respond to initial health check",
                exc_info=e
            )
            sys.exit(1)

        self.session_active = False
        self.start_time = None
        self.marker_count = 0

        # Marker manager
        self.markers = MarkerFileManager()

        # Load last-used folder if available
        last_folder = self.config.get("markers", {}).get("last_folder")
        if last_folder:
            try:
                self.set_marker_directory(last_folder)
                self.logger.info(
                    "Loaded last marker directory: %s",
                    last_folder
                )
            except Exception as e:
                self.logger.warning(
                    "Failed to restore last marker directory",
                    exc_info=e
                )

        # Callback for GUI updates
        self.on_state_change = None

    # ---------------- Marker directory ----------------
    def set_marker_directory(self, directory: str):
        self.markers.set_base_dir(directory)
        path = self.markers.new_file()

        self.config.setdefault("markers", {})["last_folder"] = directory
        save_config(self.config)

        self.logger.info("Marker directory set: %s", directory)
        self.logger.debug("New marker file created: %s", path)

        self._notify()

    # ---------------- OBS polling ----------------
    def poll(self, interval=1.0):
        try:
            status = self.req_client.get_record_status()

            if status.output_active and not self.session_active:
                self.logger.info("Recording started")
                self._start_session()

            elif not status.output_active and self.session_active:
                self.logger.info("Recording stopped")
                self._end_session()

        except Exception as e:
            self.logger.warning(
                "Failed to poll OBS",
                exc_info=e
            )

    # ---------------- Session handlers ----------------
    def _start_session(self):
        self.session_active = True
        self.start_time = int(time.time() * 1000)
        self.marker_count = 0

        self.markers.session_start()
        self.logger.info("Marker session started")
        
        self._notify()

    def _end_session(self):
        elapsed = int(time.time() * 1000) - self.start_time
        duration = self.format_elapsed(elapsed)

        self.markers.session_end(duration)
        self.session_active = False

        self.logger.info(
            "Marker session ended | Duration %s | Markers %d",
            duration,
            self.marker_count
        )

        self._notify()

    # ---------------- Marker ----------------
    def add_marker(self):
        if not self.session_active:
            self.logger.warning(
                "Marker ignored: recording not active"
            )
            return

        elapsed = int(time.time() * 1000) - self.start_time
        timestamp = self.format_elapsed(elapsed)

        self.markers.write(timestamp)
        self.marker_count += 1

        self.logger.debug(
            "Marker added at %s (count=%d)",
            timestamp,
            self.marker_count
        )

        self._notify()

    # ---------------- Utils ----------------
    @staticmethod
    def format_elapsed(ms: int) -> str:
        total_seconds = int(ms / 1000)
        h = total_seconds // 3600
        m = (total_seconds % 3600) // 60
        s = total_seconds % 60
        return f"{h:02}:{m:02}:{s:02}"

    def _notify(self):
        if self.on_state_change:
            self.on_state_change()
