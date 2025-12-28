import keyboard

class Hotkeys:
    def __init__(self, app):
        keyboard.add_hotkey("F8", app.add_marker)
