import keyboard

from app.config import load_config, save_config

class Hotkeys:
    DEFAULTS = {
        "add_marker": "F8",
    }

    def __init__(self, app):
        self.app = app
        self.config = load_config()
        self.bindings = self.config.get("hotkeys", self.DEFAULTS.copy())
        self._register_hotkeys()

    def _register_hotkeys(self):
        import keyboard
        keyboard.unhook_all()
        keyboard.add_hotkey(self.bindings["add_marker"], self.app.add_marker)

    def update_binding(self, action, new_key):
        self.bindings[action] = new_key
        self.config.setdefault("hotkeys", {})[action] = new_key
        save_config(self.config)
        self._register_hotkeys()
