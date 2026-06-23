import os
from time import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from app.utils import center_window, get_asset_path
from app.metadata import APP_INFO
from app.obs import OBSConnectionState


class MarkerGUI:
    def __init__(self, app):
        self.app = app
        self.app.on_state_change = self.schedule_refresh
        self.root = tk.Tk()

        try:
            icon_path = get_asset_path("assets/icon.png")
            app_icon = tk.PhotoImage(file=icon_path)
            self.root.iconphoto(True, app_icon)
            self._app_icon = app_icon  # Keep a reference to prevent garbage collection
        except Exception as e:
            # Don’t crash the app just because the icon failed
            self.app.logger.warning(f"Failed to load app icon: {e}")

        self.root.title(f"{APP_INFO.name} v{APP_INFO.version}")
        self.root.geometry("580x180")
        self.root.resizable(False, False)

        self.menu = tk.Menu(self.root)
        self.root.config(menu=self.menu)

        self._build_file_menu()
        self._build_about_menu()

        self.record_status_var = tk.StringVar()
        self.obs_status_var = tk.StringVar()
        self.dir_var = tk.StringVar()
        self.file_var = tk.StringVar()
        self.time_var = tk.StringVar()
        self.count_var = tk.StringVar()

        ttk.Label(self.root, textvariable=self.record_status_var).pack(anchor="w", padx=8)
        ttk.Label(self.root, textvariable=self.dir_var).pack(anchor="w", padx=8)
        ttk.Label(self.root, textvariable=self.file_var).pack(anchor="w", padx=8)
        ttk.Label(self.root, textvariable=self.time_var).pack(anchor="w", padx=8)
        ttk.Label(self.root, textvariable=self.count_var).pack(anchor="w", padx=8)

        ttk.Button(
            self.root,
            text="New Marker File (New Session)",
            command=self.new_marker_file
        ).pack(fill="x", padx=8, pady=2)

        ttk.Button(
            self.root,
            text="Add Standard Marker (Note)",
            command=self.app.add_marker
        ).pack(fill="x", padx=8, pady=(6, 2))

        self.obs_status_label = tk.Label(
            self.root,
            textvariable=self.obs_status_var,
            anchor="w"
        )
        self.obs_status_label.pack(anchor="e", padx=8)


        self.refresh()
        self.tick()

    
    # ---------------- Menus ----------------
    def _build_file_menu(self):
        file_menu = tk.Menu(self.menu, tearoff=0)
        file_menu.add_command(label="Select New Folder", command=self.select_directory)
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=self.open_settings)
        file_menu.add_command(label="Quit", command=self.root.quit)
        self.menu.add_cascade(label="File", menu=file_menu)

    def _build_about_menu(self):
        about_menu = tk.Menu(self.menu, tearoff=0)
        about_menu.add_command(label="About", command=self.show_about)
        self.menu.add_cascade(label="About", menu=about_menu)

    # ---------- UI actions ----------
    def select_directory(self):
        directory = filedialog.askdirectory(
            title="Select Marker Folder"
        )
        if directory:
            self.app.set_marker_directory(directory)

    def new_marker_file(self):
        if self.app.session_active:
            messagebox.showwarning("Recording Active!",
                           "Stop recording before starting a new marker file.")
            return

        if not self.app.markers.base_dir:
            messagebox.showwarning("No Marker Folder",
                           "Select a marker folder before starting a new marker file.")
            return

        self.app.new_marker_file()
        self.refresh()

    def show_about(self):
        messagebox.showinfo("About MarkerMate",
                            f"{APP_INFO.name} v{APP_INFO.version}\n\n"
                            f"{APP_INFO.description}\n"
                            f"Author: {APP_INFO.author}\n"
                            f"Website: {APP_INFO.repo_url}")       

    def open_settings(self):
        if getattr(self, "_settings_window", None):
            self._settings_window.lift()
            return

        from app.gui.settings_window import SettingsWindow
        self._settings_window = SettingsWindow(
            parent=self.root,
            app=self.app,
            on_close=self._on_settings_closed
        )

    def _on_settings_closed(self):
        self._settings_window = None

    # ---------- UI refresh ----------
    def schedule_refresh(self):
         self.root.after(0, self.refresh)

    def refresh(self):
        state = self.app.obs.state

        if state == OBSConnectionState.CONNECTED:
            self.obs_status_var.set("● OBS Connected")
            self.obs_status_label.config(fg="green")
        elif state == OBSConnectionState.CONNECTING:
            self.obs_status_var.set("◐ OBS Connecting…")
            self.obs_status_label.config(fg="orange")
        elif state == OBSConnectionState.AUTH_ERROR:
            self.obs_status_var.set("○ OBS Auth Error - Check Settings")
            self.obs_status_label.config(fg="red")        
        else:
            self.obs_status_var.set("○ OBS Not running")
            self.obs_status_label.config(fg="red")


        status = "● RECORDING" if self.app.session_active else "○ IDLE"
        self.record_status_var.set(f"Status: {status}")

        self.dir_var.set(
            f"Folder: {self.app.markers.base_dir or '—'}"
        )

        self.file_var.set(
            f"File: {self.app.markers.current_filename or '—'}"
        )

        self.count_var.set(
            f"Markers: {self.app.marker_count}"
        )

    def tick(self):
        if self.app.session_active and self.app.start_time:
            elapsed = int(time() * 1000) - self.app.start_time
            self.time_var.set(
                f"Duration: {self.app.format_elapsed(elapsed)}"
            )
        else:
            self.time_var.set("Duration: 00:00:00")

        self.root.after(500, self.tick)


    def run(self):
        self.root.mainloop()
