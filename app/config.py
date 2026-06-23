import os
import json
import logging
import time
from collections.abc import MutableMapping
from appdirs import user_config_dir


logger = logging.getLogger("MarkerMate")


class OBSMarkerConfig(MutableMapping):
    def __init__(self, app_name="MarkerMate"):
        self.config_dir = os.path.join(user_config_dir(app_name), "config")
        os.makedirs(self.config_dir, exist_ok=True)
        self.config_path = os.path.join(self.config_dir, "config.json")
        self._cfg = self._load()

    # MutableMapping methods
    def __getitem__(self, key):
        return self._cfg[key]

    def __setitem__(self, key, value):
        self._cfg[key] = value
        self.save()

    def __delitem__(self, key):
        del self._cfg[key]
        self.save()

    def __iter__(self):
        return iter(self._cfg)

    def __len__(self):
        return len(self._cfg)

    # Core methods
    def _load(self) -> dict:
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
            except json.JSONDecodeError:
                self._backup_corrupt_config()
                return {}

            if isinstance(data, dict):
                return data

            self._backup_corrupt_config()
            return {}
        return {}

    def _backup_corrupt_config(self):
        if not os.path.exists(self.config_path):
            return None

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        backup_path = f"{self.config_path}.corrupt-{timestamp}"

        counter = 2
        while os.path.exists(backup_path):
            backup_path = f"{self.config_path}.corrupt-{timestamp}-{counter}"
            counter += 1

        os.replace(self.config_path, backup_path)
        logger.warning("Invalid config moved to %s; starting with defaults", backup_path)
        return backup_path

    def save(self):
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self._cfg, f, indent=2)

    def reset(self):
        if os.path.exists(self.config_path):
            os.remove(self.config_path)
        self._cfg = {}
        return self._cfg

    def ensure_obs_config(self) -> dict:
        obs_cfg = self._cfg.setdefault("obs", {})
        obs_cfg.setdefault("host", "localhost")
        obs_cfg.setdefault("port", 4455)
        obs_cfg.setdefault("password", None)
        self.save()
        return self._cfg
