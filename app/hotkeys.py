import keyboard
from app.config import OBSMarkerConfig

class Hotkeys:
    DEFAULTS = {
        "marker_note": "F8",
        "marker_custom_1": "F9",
        "marker_custom_2": "F10",
        "marker_custom_3": "F11",
        "new_file": "F12",
    }

    def __init__(self, app, config: OBSMarkerConfig):
        self.app = app
        self.config = config
        self.bindings = self.config.setdefault("hotkeys", self.DEFAULTS.copy())
        self._register_hotkeys()

    def _register_hotkeys(self):
        keyboard.unhook_all()
        for action, key in self.bindings.items():
            keyboard.add_hotkey(key, self._dispatch, args=(action,))

    def _dispatch(self, action):
        if action.startswith("marker_"):
            marker_type = action.removeprefix("marker_")
            self.app.add_marker(marker_type)
        elif action == "new_file":
            self.app.new_marker_file()

    def update_binding(self, action, new_key):
        """Update a hotkey binding and persist it."""
        self.bindings[action] = new_key
        self.config["hotkeys"] = self.bindings
        self.config.save()
        self._register_hotkeys()
