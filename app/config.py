import os
import json
from collections.abc import MutableMapping
from appdirs import user_config_dir


class OBSMarkerConfig(MutableMapping):
    def __init__(self, app_name="OBSMarkers"):
        self.config_dir = user_config_dir(app_name, False)
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
            with open(self.config_path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {}

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
