import time

from app.obs import OBSClient
from app.markers import MarkerFileManager
from app.config import load_config, save_config


class MarkerApp:
    def __init__(self, logger):
        self.logger = logger
        self.on_state_change = None

        self.config = load_config()

        self.obs = OBSClient(logger)

        self.session_active = False
        self.start_time = None
        self.marker_count = 0

        self.markers = MarkerFileManager()

        last_folder = self.config.get("markers", {}).get("last_folder")
        if last_folder:
            try:
                self.set_marker_directory(last_folder)
            except Exception:
                self.logger.exception("Failed to restore marker folder")


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
    def poll(self):
        if not self.obs.is_connected():
            was_recording = self.session_active
            self.obs.connect()

            if was_recording and not self.obs.is_connected():
                self.logger.warning(
                    "OBS disconnected during recording; ending session"
                )
                self._end_session()

            self._notify()
            return

        status = self.obs.call(self.obs.client.get_record_status)

        if status is None:
            if self.session_active:
                self.logger.warning(
                    "Lost OBS during recording; ending session"
                )
                self._end_session(reason="obs_disconnected")

            self._notify()
            return

        if status.output_active and not self.session_active:
            self._start_session()
        elif not status.output_active and self.session_active:
            self._end_session()


    # ---------------- Session handlers ----------------
    def _start_session(self):
        self.session_active = True
        self.start_time = int(time.time() * 1000)
        self.marker_count = 0

        self.markers.session_start()
        self.logger.info("Marker session started")
        
        self._notify()

    def _end_session(self, reason="stopped"):
        elapsed = int(time.time() * 1000) - self.start_time
        duration = self.format_elapsed(elapsed)

        self.markers.session_end(duration)
        self.session_active = False

        self.logger.info(
            "Marker session ended | Duration %s | Markers %d",
            duration,
            self.marker_count,
            f"{reason}"
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
        callback = getattr(self, "on_state_change", None)
        if callback:
            callback()

