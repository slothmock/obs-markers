import tkinter as tk
from tkinter import ttk, messagebox

from app.gui.utils import center_window

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, app, on_close):
        super().__init__(parent)
        self.app = app
        self.on_close = on_close

        self.title("Settings")
        self.geometry("300x300")
        self.resizable(False, False)

        center_window(self)

        self.protocol("WM_DELETE_WINDOW", self._close)

        self._build_ui()

    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self._build_ws_tab(notebook)
        self._build_hotkeys_tab(notebook)

    def _build_ws_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="OBS WebSocket Server")

        ttk.Label(frame, text="Host:").grid(row=0, column=0, sticky="w", pady=5, padx=5)
        ttk.Label(frame, text="Port:").grid(row=1, column=0, sticky="w", pady=5, padx=5)
        ttk.Label(frame, text="Password:").grid(row=2, column=0, sticky="w", pady=5, padx=5)

        self.host_var = tk.StringVar(value=self.app.config["obs"]["host"])
        self.port_var = tk.IntVar(value=self.app.config["obs"]["port"])
        self.pass_var = tk.StringVar(value=self.app.config["obs"].get("password", ""))

        ttk.Entry(frame, textvariable=self.host_var).grid(row=0, column=1, sticky="we")
        ttk.Spinbox(frame, from_=1, to=65535, increment=1, textvariable=self.port_var, width=8, wrap=True).grid(row=1, column=1, sticky="we")
        ttk.Entry(frame, textvariable=self.pass_var, show="*").grid(row=2, column=1, sticky="we")

        frame.columnconfigure(1, weight=1)

        ttk.Button(frame, text="Apply", command=self.apply_ws_settings).grid(row=3, column=0, columnspan=2, pady=10)

    def apply_ws_settings(self):
        host = self.host_var.get().strip()
        port = self.port_var.get()

        if not host or not (1 <= port <= 65535):
            messagebox.showerror("Invalid settings", "Host or port is invalid.")
            return

        # Merge changes into OBS config
        self.app.config["obs"].update({
            "host": host,
            "port": port,
            "password": self.pass_var.get() or None
        })
        self.app.config.save()

        self.app.update_obs_settings(
            host=self.host_var.get().strip(),
            port=self.port_var.get(),
            password=self.pass_var.get() or None
        )

        messagebox.showinfo("Settings saved", "OBS WebSocket settings applied successfully.")

    def _build_hotkeys_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Hotkeys")

        self.hotkeys = self.app.hotkeys
        self.hotkey_labels = {}
        self.hotkey_name_labels = {}

        for row, (action, key) in enumerate(self.hotkeys.bindings.items()):
            if action == "new_file":
                name = "New Marker File"
            else:
                name = self.hotkeys.get_marker_label(action)

            name_label = ttk.Label(frame, text=name)
            name_label.grid(row=row, column=0, sticky="w", pady=6)

            value_label = ttk.Label(frame, text=key, width=12, anchor="e")
            value_label.grid(row=row, column=1, padx=5)

            self.hotkey_name_labels[action] = name_label
            self.hotkey_labels[action] = value_label

            ttk.Button(
                frame,
                text="Modify",
                command=lambda a=action: self._open_hotkey_dialog(a)
            ).grid(row=row, column=2, padx=5)

        frame.columnconfigure(0, weight=1)

        buttons = ttk.Frame(frame)
        buttons.grid(
            row=len(self.hotkeys.bindings),
            column=0,
            columnspan=3,
            pady=15,
            sticky="ew"
        )

        buttons.columnconfigure(0, weight=1)
        buttons.columnconfigure(1, weight=1)

        ttk.Button(
            buttons,
            text="Reset to Defaults",
            command=self._reset_hotkeys
        ).grid(row=0, column=0, sticky="e", padx=5, pady=5)

    def _open_hotkey_dialog(self, action):
        is_custom = action.startswith("custom_")

        dialog = tk.Toplevel(self)
        dialog.title("Modify Hotkey / Label" if is_custom else "Modify Hotkey")
        dialog.geometry("260x180")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()
        center_window(dialog)


        container = ttk.Frame(dialog, padding=12)
        container.pack(fill="both", expand=True)

        # Title
        ttk.Label(
            container,
            text=action.replace("_", " ").title(),
            font=("Segoe UI", 11, "bold")
        ).grid(row=0, column=0, columnspan=2, pady=(0, 12))

        # Hotkey
        key_var = tk.StringVar(value=self.hotkeys.bindings[action])
        key_label = ttk.Label(container, textvariable=key_var, font=("Segoe UI", 10, "bold"))
        key_label.grid(row=1, column=1, sticky="we", padx=8)

        capture_active = {"on": False}

        def on_key(event):
            if not capture_active["on"]:
                return
            mods = []
            if event.state & 0x0004:
                mods.append("ctrl")
            if event.state & 0x0001:
                mods.append("shift")
            if event.state & 0x0008:
                mods.append("alt")
            mods.append(event.keysym.lower())
            key_var.set("+".join(mods).upper())
            capture_active["on"] = False
            dialog.unbind("<Key>")

        def arm_capture():
            capture_active["on"] = True
            key_var.set("Press keys…")
            dialog.bind("<Key>", on_key)

        ttk.Button(container, text="Change Key", command=arm_capture, padding=2).grid(
            row=1, column=0, columnspan=1, pady=6
        )

        # Custom marker label
        label_var = None
        if is_custom:
            ttk.Label(container, text="Marker Label:").grid(row=3, column=0, sticky="w", pady=2)
            label_var = tk.StringVar(value=self.hotkeys.get_marker_label(action))
            ttk.Entry(container, textvariable=label_var, width=24).grid(row=3, column=1, sticky="e", pady=2)

        # -------- Action Buttons --------
        btn_frame = ttk.Frame(container)
        btn_frame.grid(row=4, column=0, columnspan=2, pady=(16, 0))
        
        ttk.Button(btn_frame, text="Apply", command=lambda: apply()).pack(side="left", padx=6)
        ttk.Button(btn_frame, text="Cancel", command=dialog.destroy).pack(side="left")

        container.columnconfigure(0, weight=1)
        container.columnconfigure(1, weight=1)

        # -------- Apply logic --------
        def apply():
            new_key = key_var.get()
            if new_key not in ("Press keys…", "", None):
                self.hotkeys.update_binding(action, new_key)

                if is_custom:
                    label = label_var.get().strip()
                    if label:
                        self.hotkeys.set_marker_label(action, label)

                self.hotkey_labels[action].config(text=new_key)
                self._refresh_hotkey_labels()
                dialog.destroy()



    def _refresh_hotkey_labels(self):
        for action, key_label in self.hotkey_labels.items():
            key_label.config(text=self.hotkeys.bindings.get(action, ""))

            if action != "new_file":
                label = self.hotkeys.get_marker_label(action)
                self.hotkey_name_labels[action].config(text=label)

    def _reset_hotkeys(self):
        if not messagebox.askyesno(
            "Confirm Reset",
            "Reset all hotkeys and marker labels to default?"
        ):
            return

        # Reset key bindings
        for action, key in self.hotkeys.DEFAULT_KEYS.items():
            self.hotkeys.update_binding(action, key)
            self.hotkey_labels[action].config(text=self.hotkeys.bindings[action])

        # Reset marker labels
        for marker_type, default_label in self.hotkeys.DEFAULT_MARKER_LABELS.items():
            self.hotkeys.set_marker_label(marker_type, default_label)
            self.hotkey_name_labels[marker_type].config(text=default_label)

        messagebox.showinfo(
            "Hotkeys reset",
            "All hotkeys and marker labels have been reset to default."
        )

    def _close(self):
        self.on_close()
        self.destroy()
