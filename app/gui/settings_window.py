import tkinter as tk
from tkinter import ttk, messagebox

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, app, on_close):
        super().__init__(parent)
        self.app = app
        self.on_close = on_close

        self.title("Settings")
        self.geometry("360x240")
        self.resizable(False, False)

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

        self.app.update_obs_settings(host=host, port=port, password=self.pass_var.get() or None)
        messagebox.showinfo("Settings saved", "OBS WebSocket settings applied successfully.")

    def _build_hotkeys_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="Hotkeys")

        self.hotkeys = self.app.hotkeys
        self.hotkey_labels = {}

        for row, (action, key) in enumerate(self.hotkeys.bindings.items()):
            label = action.replace("_", " ").title()

            ttk.Label(frame, text=label).grid(
                row=row, column=0, sticky="w", pady=6
            )

            value_label = ttk.Label(frame, text=key, width=12, anchor="center")
            value_label.grid(row=row, column=1, padx=5)

            self.hotkey_labels[action] = value_label

            ttk.Button(
                frame,
                text="Customize",
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
        ).grid(row=0, column=0, sticky="e", padx=5)



    def _open_hotkey_dialog(self, action):
        dialog = tk.Toplevel(self)
        dialog.title("Set Hotkey")
        dialog.geometry("300x140")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        ttk.Label(
            dialog,
            text=f"Press new hotkey for:\n{action.replace('_', ' ').title()}",
            justify="center"
        ).pack(pady=10)

        key_var = tk.StringVar(value="Waiting for input…")

        key_label = ttk.Label(dialog, textvariable=key_var, font=("Segoe UI", 10, "bold"))
        key_label.pack(pady=5)

        def on_key(event):
            parts = []
            if event.state & 0x0004:
                parts.append("ctrl")
            if event.state & 0x0001:
                parts.append("shift")
            if event.state & 0x0008:
                parts.append("alt")

            parts.append(event.keysym.lower())
            key_var.set("+".join(parts).upper())

        dialog.bind("<Key>", on_key)

        def apply():
            new_key = key_var.get()
            if "Waiting" in new_key:
                return

            self.hotkeys.update_binding(action, new_key)
            self.hotkey_labels[action].config(text=new_key)
            dialog.destroy()

        ttk.Button(dialog, text="Apply", command=apply).pack(pady=10)

    def _reset_hotkeys(self):
        if not messagebox.askyesno(
            "Confirm Reset",
            "Reset all hotkeys to defaults?"
        ):
            return

        for action, key in self.hotkeys.DEFAULTS.items():
            self.hotkeys.update_binding(action, key)
            self.hotkey_labels[action].config(text=key)

        messagebox.showinfo(
            "Hotkeys reset",
            "All hotkeys have been reset to defaults."
        )


    def _close(self):
        self.on_close()
        self.destroy()
