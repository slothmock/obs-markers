import sys
import time
import obsws_python as obs
from app.markers import MarkerFileManager
from app.config import load_config, save_config


class MarkerApp:
    def __init__(self):
        # Config
        self.config = load_config()

        # OBS ReqClient
        try:
            self.req_client = obs.ReqClient(host='localhost', port=4455)
        except Exception as e:
            print(f"[ERROR] Failed to create OBS request client: {e}", flush=True)
            sys.exit(1)

        # Fail-fast check
        try:
            stats = self.req_client.get_stats()
            print(f"[INFO] OBS connected. CPU {stats.cpu_usage:.2f}%, Memory {stats.memory_usage:.2f} MB", flush=True)
        except Exception as e:
            print("[ERROR] OBS did not respond.", flush=True)
            print(e, flush=True)
            sys.exit(1)

        # Session state
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
            except Exception:
                pass

        # Callback for GUI updates
        self.on_state_change = None

    # ---------------- Marker directory ----------------
    def set_marker_directory(self, directory: str):
        self.markers.set_base_dir(directory)
        self.markers.new_file()
        # Save to config
        self.config.setdefault("markers", {})["last_folder"] = directory
        save_config(self.config)
        self._notify()

    # ---------------- OBS polling ----------------
    def poll(self, interval=1.0):
        try:
            status = self.req_client.get_record_status()
            if status.output_active and not self.session_active:
                self._start_session()
            elif not status.output_active and self.session_active:
                self._end_session()
        except Exception as e:
            print(f"[WARN] Failed to poll OBS: {e}", flush=True)

    # ---------------- Session handlers ----------------
    def _start_session(self):
        self.session_active = True
        self.start_time = int(time.time() * 1000)
        self.marker_count = 0
        self.markers.session_start()
        self._notify()

    def _end_session(self):
        elapsed = int(time.time() * 1000) - self.start_time
        self.markers.session_end(self.format_elapsed(elapsed))
        self.session_active = False
        self._notify()

    # ---------------- Marker ----------------
    def add_marker(self):
        if not self.session_active:
            print("[WARN] Not recording. Marker not added.", flush=True)
            return
        elapsed = int(time.time() * 1000) - self.start_time
        self.markers.write(self.format_elapsed(elapsed))
        self.marker_count += 1
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
