import keyboard
from app.config import OBSMarkerConfig

class Hotkeys:
    DEFAULT_KEYS = {
        "note": "F8",
        "custom_1": "F9",
        "custom_2": "F10",
        "custom_3": "F11",
        "new_file": "F12",
    }
    DEFAULT_MARKER_LABELS = {
        "note": "Note",
        "custom_1": "Custom 1",
        "custom_2": "Custom 2",
        "custom_3": "Custom 3"
    }

    def __init__(self, app, config: OBSMarkerConfig):
        self.app = app
        self.config = config
        self.bindings = self.config.setdefault("hotkeys", self.DEFAULT_KEYS.copy())
        self._register_hotkeys()

    def _register_hotkeys(self):
        keyboard.unhook_all()
        for action, key in self.bindings.items():
            keyboard.add_hotkey(key, self._dispatch, args=(action))

    def _dispatch(self, action):
        if action == "new_file":
            self.app.new_marker_file()
        else:
            self.app.add_marker(action)

         
    def update_binding(self, action, new_key):
        """Update a hotkey binding and persist it."""
        self.bindings[action] = new_key
        self.config["hotkeys"] = self.bindings
        self.config.save()
        self._register_hotkeys()

    def get_marker_label(self, marker_type: str) -> str:
        return self.config.setdefault("marker_types", {}).get(marker_type, marker_type)

    def set_marker_label(self, marker_type: str, label: str):
        self.config.setdefault("marker_types", {})[marker_type] = label
        self.config.save()
