import time

from app.obs import OBSClient
from app.marker_files import MarkerFileManager
from app.hotkeys import Hotkeys
from app.config import OBSMarkerConfig


class MarkerApp:
    def __init__(self, logger):
        self.logger = logger
        self.on_state_change = None

        self.config = OBSMarkerConfig()
        self.config.ensure_obs_config()
        
        self.config.setdefault("hotkeys", Hotkeys.DEFAULT_KEYS.copy())
        self.config.setdefault("marker_types", {
            "note": "Note",
            "custom_1": "Custom 1",
            "custom_2": "Custom 2",
            "custom_3": "Custom 3",
        })

        obs_cfg = self.config["obs"]
        self.obs = OBSClient(logger=self.logger,
                             host=obs_cfg['host'],
                             port=obs_cfg['port'],
                             password=obs_cfg['password']
                             )
        
        self.hotkeys = Hotkeys(self, self.config)

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

        self.config.setdefault("markers", {})["last_folder"] = directory
        self.config.save()

        self.logger.info("Marker directory set: %s", directory)

        self._notify()

    def new_marker_file(self) -> str | None:
        if self.session_active:
            self.logger.warning("New marker file ignored: recording is active")
            return None

        if not self.markers.base_dir:
            self.logger.warning("New marker file ignored: marker directory not set")
            return None

        path = self.markers.new_file()
        self.logger.debug("New marker file created: %s", path)
        self._notify()
        return path

    # ---------------- OBS Handlers ----------------
    def poll(self):
        if not self.obs.is_connected():
            was_recording = self.session_active
            self.obs.connect()

            if was_recording and not self.obs.is_connected():
                self._handle_disconnection()

            self._notify()
            return

        status = self.obs.call(self.obs.client.get_record_status)

        if status is None:
            if self.session_active:
                self._handle_disconnection()
            self._notify()
            return

        if status.output_active and not self.session_active:
            self._start_session()
        elif not status.output_active and self.session_active:
            self._end_session()

    def _handle_disconnection(self):
        self.logger.warning("OBS disconnected during recording; ending session")
        self._end_session(reason="obs_disconnected")

    def update_obs_settings(self, host, port, password):
        self.logger.info("Updating OBS connection settings")

        self.config["obs"].update({
            "host": host,
            "port": port,
            "password": password
        })
        self.config.save()

        self.obs.update_settings(host, port, password)
        self.obs.reset()
        self.obs.connect()

        self._notify()

        
    # ---------------- Session handlers ----------------
    def _start_session(self):
        self.session_active = True
        self.start_time = int(time.time() * 1000)
        self.marker_count = 0

        if self.markers.base_dir:
            self.markers.new_file()
        else:
            self.logger.warning("Marker session started without a marker directory")

        self.markers.session_start()
        self.logger.info("Marker session started")
        
        self._notify()

    def _end_session(self, reason="stopped"):
        elapsed = int(time.time() * 1000) - self.start_time
        duration = self.format_elapsed(elapsed)

        self.markers.session_end(duration)
        self.session_active = False

        self.logger.info(
            f"Marker session ended | Duration {duration} | Markers {self.marker_count}\nReason: {reason}"
        )

        self._notify()

    def add_marker(self, marker_type="note"):
        if not self.session_active:
            self.logger.warning("Marker ignored: recording not active")
            return

        elapsed = int(time.time() * 1000) - self.start_time
        timestamp = self.format_elapsed(elapsed)

        label = self.config["marker_types"].get(marker_type, marker_type.title())
        label = f"{label.removeprefix('Marker ')}"

        self.markers.write_marker(timestamp, label)
        self.marker_count += 1

        self.logger.debug(
            "Marker added at %s [%s] (count=%d)",
            timestamp,
            marker_type,
            self.marker_count
        )

        self._notify()


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



