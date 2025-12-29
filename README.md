# OBS Markers ![Version](https://img.shields.io/badge/version-0.1.0-blue) ![Python](https://img.shields.io/badge/python-3.11+-blue) ![License](https://img.shields.io/badge/license-MIT-green)

**OBS Markers** is a lightweight utility for logging timestamp markers while recording with [OBS Studio](https://obsproject.com/). Works with any OBS-supported recording format, automatically tracks recording sessions, writes timestamps to marker files, and provides a simple GUI. 

> ⚠️ **Pre-alpha release: Breaking changes may occur before v1.0.**

---

## Features

- Automatically detects OBS recording start/stop  
- Logs marker timestamps to a text file per session  
- Supports recording to any OBS-supported file format while still logging markers  
- Auto-named marker files with timestamps (`markers_YYYY-MM-DD_HH-MM-SS.txt`)  
- GUI showing recording status, marker count, and elapsed time  
- Persistent configuration stored in OS-appropriate directories using `appdirs`  
- Cross-platform support (Windows, macOS, Linux)  
- Ready for standalone `.exe` builds via PyInstaller  

---

## Installation

### Prerequisites

- Python 3.11+  
- [OBS Studio](https://obsproject.com/) with **WebSocket 5.x** enabled  
- Required Python packages:

```bash
pip install -r requirements.txt
````

`requirements.txt`:

```
obsws_python
keyboard
appdirs
```

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

* First launch will prompt you to select a folder for marker files
* The GUI displays recording status, marker file, elapsed time, and marker count

---

## Usage

### Hotkeys

| Action               | Default Hotkey         |
| -------------------- | ---------------------- |
| Add Marker           | `F8`                   |
| Select Marker Folder | `F12`                  |
| Quit                 | File → Quit |

> **Note:** Hotkeys are currently fixed but will be customizable in future versions.

### GUI

* Shows current recording status, marker folder/file, elapsed time, and marker count
* "Add Marker" button logs a timestamp to the current marker file
* "File" menu allows selecting marker folder and quitting the app
* "About" menu shows version and author info


## Marker Files

* Stored in the user-selected folder
* Auto-named format: `markers_YYYY-MM-DD_HH-MM-SS.txt`
* Session start/end markers are written automatically
* Manual markers are appended as individual timestamp lines for easy reference
---

### example_markers.txt:

```
=== SESSION START 2025-12-29 16:29:09 ===
00:00:08
00:00:12
=== SESSION END | Duration: 00:00:16 ===
```


## Configuration

Configuration is stored using `appdirs` in the OS-appropriate config folder:

| OS      | Example Config Location                                                |
| ------- | ---------------------------------------------------------------------- |
| Windows | `C:\Users\<username>\AppData\Roaming\OBSMarkers\config.json`           |
| macOS   | `/Users/<username>/Library/Application Support/OBSMarkers/config.json` |
| Linux   | `/home/<username>/.config/OBSMarkers/config.json`                      |

Example `config.json`:

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

Create a standalone Windows executable using PyInstaller:

```bash
pip install pyinstaller
pyinstaller --onefile -w main.py
```

* `-w` disables the console window (useful for GUI-only applications)
* Run PyInstaller in the project root so that relative imports work

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
