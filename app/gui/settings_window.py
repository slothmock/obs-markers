import tkinter as tk
from tkinter import ttk, messagebox

class SettingsWindow(tk.Toplevel):
    def __init__(self, parent, app, on_close):
        super().__init__(parent)
        self.app = app
        self.on_close = on_close

        self.title("Settings")
        self.geometry("420x300")
        self.resizable(False, False)

        self.protocol("WM_DELETE_WINDOW", self._close)

        self._build_ui()

    def _build_ui(self):
        notebook = ttk.Notebook(self)
        notebook.pack(fill="both", expand=True, padx=10, pady=10)

        self._build_ws_tab(notebook)

    def _build_ws_tab(self, notebook):
        frame = ttk.Frame(notebook)
        notebook.add(frame, text="OBS WebSocket Server")

        ttk.Label(frame, text="Host").grid(row=0, column=0, sticky="w", pady=5)
        ttk.Label(frame, text="Port").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Label(frame, text="Password").grid(row=2, column=0, sticky="w", pady=5)

        self.host_var = tk.StringVar(value=self.app.config["obs"]["host"])
        self.port_var = tk.IntVar(value=self.app.config["obs"]["port"])
        self.pass_var = tk.StringVar(value=self.app.config["obs"].get("password", ""))

        ttk.Entry(frame, textvariable=self.host_var).grid(row=0, column=1, sticky="ew")
        ttk.Entry(frame, textvariable=self.port_var).grid(row=1, column=1, sticky="ew")
        ttk.Entry(frame, textvariable=self.pass_var, show="*").grid(row=2, column=1, sticky="ew")

        frame.columnconfigure(1, weight=1)

        ttk.Button(
            frame,
            text="Apply",
            command=self.apply
        ).grid(row=3, column=0, columnspan=2, pady=10)

    def apply(self):
        host = self.host_var.get().strip()
        port = self.port_var.get()

        if not host or not (1 <= port <= 65535):
            messagebox.showerror("Invalid settings", "Host or port is invalid.")
            return

        self.app.update_obs_settings(
            host=host,
            port=port,
            password=self.pass_var.get() or None
        )

        messagebox.showinfo("Settings saved", "Settings applied successfully.")

    def _close(self):
        self.on_close()
        self.destroy()
