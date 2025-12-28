# OBS Markers

**OBS Markers** is a lightweight utility for logging markers while recording with OBS Studio. It automatically tracks recording sessions, writes timestamps to marker files, and provides a simple GUI. Ideal for streamers, content creators, or anyone needing precise marker tracking.

---

## Features

- Automatically detects OBS recording start/stop  
- Logs marker timestamps to a text file per session  
- Auto-named marker files with timestamps  
- GUI showing recording status, marker count, and elapsed time  
- Persistent configuration stored in OS-appropriate directories using `appdirs`  
- Cross-platform support (Windows/Linux/macOS)  
- Ready for standalone `.exe` builds via PyInstaller  

---

## Installation

### Prerequisites

- Python 3.11+  
- [OBS Studio](https://obsproject.com/) with **WebSocket 5.x** enabled  
- Required Python packages:  

```bash
pip install obsws-python keyboard appdirs
````

---

### Clone the repository

```bash
git clone https://github.com/slothmock/obs-markers.git
cd obs-markers
```

---

### Run the app

```bash
python -m app
```

* First launch will prompt to select a folder for marker files
* The GUI displays recording status, marker file, elapsed time, and marker count

---

## Usage

### Hotkeys

| Action               | Default Hotkey         |
| -------------------- | ---------------------- |
| Add Marker           | `F8`                   |
| Select Marker Folder | `F12`                  |
| Quit                 | GUI Menu → File → Quit |

> Hotkeys are currently fixed but can be customized in future versions.

### GUI

* Shows current recording status, marker folder/file, elapsed time, and marker count
* "Add Marker" button logs a timestamp to the current marker file
* "File" menu allows selecting marker folder and quitting the app
* "About" menu shows version and author info

---

## Marker Files

* Stored in the user-selected folder
* Auto-named format: `markers_YYYY-MM-DD_HH-MM-SS.txt`
* Session start/end markers are written automatically
* Manual markers are appended with timestamps

Example:

```
=== SESSION START 2025-12-28 20:15:00 ===
00:00:05
00:01:12
=== SESSION END | Duration: 00:15:34 ===
```

---

## Configuration

* Configuration is stored using `appdirs` in the OS-appropriate config folder:

| OS      | Example Config Location                                                |
| ------- | ---------------------------------------------------------------------- |
| Windows | `C:\Users\<username>\AppData\Roaming\OBSMarkers\config.json`           |
| macOS   | `/Users/<username>/Library/Application Support/OBSMarkers/config.json` |
| Linux   | `/home/<username>/.config/OBSMarkers/config.json`                      |

* Stores the last-used marker folder and default hotkeys:

```json
{
  "markers": {
    "last_folder": "C:/Users/sloth/Videos/Markers"
  },
  "hotkeys": {
    "add_marker": "F8",
    "select_folder": "F12"
  }
}
```

---

## Packaging as an EXE

You can create a standalone Windows executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile -w app.py
```

* `-w` disables the console window (useful for GUI-only applications)

---

## Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature/my-feature`)
3. Commit your changes (`git commit -am 'Add feature'`)
4. Push to the branch (`git push origin feature/my-feature`)
5. Open a Pull Request

---

## License

MIT License © 2025 Jordan 'sloth' Mock
