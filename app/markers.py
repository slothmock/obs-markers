import os
import time


class MarkerFileManager:
    def __init__(self):
        self.base_dir: str | None = None
        self.current_filename: str | None = None

    # -------- Directory management --------
    def set_base_dir(self, directory: str):
        self.base_dir = os.path.expanduser(directory)
        os.makedirs(self.base_dir, exist_ok=True)

    # -------- File lifecycle --------
    def new_file(self) -> str:
        if not self.base_dir:
            raise RuntimeError("Marker directory not set")

        ts = time.strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"markers_{ts}.txt"
        path = os.path.join(self.base_dir, filename)

        # Touch file immediately
        with open(path, "a"):
            pass

        self.current_filename = filename
        return path

    # -------- Writing --------
    def write(self, line: str):
        if not self.current_file:
            return

        with open(self.current_file, "a") as f:
            f.write(line + "\n")

    def session_start(self):
        self.write(
            f"=== SESSION START {time.strftime('%Y-%m-%d %H:%M:%S')} ==="
        )

    def session_end(self, duration: str):
        self.write(
            f"=== SESSION END | Duration: {duration} ==="
        )
