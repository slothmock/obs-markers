# OBS Markers

![GitHub Release](https://img.shields.io/github/v/release/slothmock/obs-markers?include_prereleases)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)


<table>
  <tr>
    <td align="center" colspan="2">
      <img src="docs/gui-main.png" width="100%">
    </td>
  </tr>
  <tr>
    <td align="center" width="50%">
      <strong>OBS WebSocket</strong><br>
      <img src="docs/gui-settings-obs.png" width="300">
    </td>
    <td align="center" width="50%">
      <strong>Hotkeys</strong><br>
      <img src="docs/gui-settings-hotkeys.png" width="300">
    </td>
  </tr>
</table>



**OBS Markers** is a lightweight desktop utility for logging timestamp markers while recording with [OBS Studio](https://obsproject.com/).

It automatically detects when OBS starts and stops recording, tracks the session duration, and writes timestamped markers to a text file via configurable hotkeys - making it easy to flag key moments or specific events during long recordings for later editing.

> ⚠️ **Pre-alpha software**
> The app is stable for daily use but the data format and features may still change before v1.0.

---

## Features

* Automatic detection of OBS recording start and stop
* One marker file per recording session
* Instant timestamp markers via hotkey or button
* Customizable hotkeys via the Settings panel
* Persistent configuration stored in OS-appropriate locations
* Clear GUI showing:

  * OBS connection status
  * Recording status
  * Elapsed recording time
  * Active marker file
  * Marker count
* Graceful handling when OBS is closed, unavailable, or restarted
* Standalone Windows `.exe` builds available

---

## Installation

### Windows (Recommended)

Download the latest standalone executable from the [Releases page](https://github.com/slothmock/obs-markers/releases).  
No Python installation required.

---

### Running from source (Developers)

#### Prerequisites

* Python **3.11+**
* [OBS Studio](https://obsproject.com/) with **WebSocket 5.x** enabled

#### Clone the repository

```bash
git clone https://github.com/slothmock/obs-markers.git
cd obs-markers
```

#### Install dependencies

```bash
pip install -r requirements.txt
```

#### Run the app

```bash
python -m app
```

---

## First-time Setup

1. Open **OBS Studio**
2. Enable the WebSocket server
   (`Tools -> WebSocket Server Settings`)
3. Launch **OBS Markers**
4. Select a folder for marker files when prompted (`File -> Select New Folder`)
5. Start recording in OBS (via UI button or hotkey) - the session will be automatically detected

---

## Usage

### Hotkeys

Hotkeys are configurable in the menu:  
**File -> Settings -> Hotkeys**.

| Action     | Default |
| ---------- | ------- |
| New File   | `F12`   |
| Add Marker | `F8`    |

Changes apply immediately without restarting the app.

---

### Marker Files

* Stored in the user-selected folder
* Automatically named using the recording start time:

  ```
  markers_YYYY-MM-DD_HH-MM-SS.txt
  ```
* Session start and end markers are written automatically
* Manual markers are appended as timestamps

Example:

```txt
=== SESSION START 2025-12-29 16:29:09 ===
00:00:08
00:00:12
=== SESSION END | Duration: 00:00:16 ===
```

## Settings

### OBS WebSocket Server

Connection settings can be edited at any time by selecting  
**File -> Settings -> OBS WebSocket Server**:

* Host
* Port
* Password (if enabled)

Changes take effect immediately, with automatic reconnection attempts.

## Configuration

Configuration is stored using `appdirs` in the OS-appropriate config directory.

| OS      | Example path                                           | Tested
| ------- | ------------------------------------------------------ | ----- 
| Windows | `C:\Users\<user>\AppData\Local\OBSMarkers\config.json` | [ x ]
| macOS   | `~/Library/Application Support/OBSMarkers/config.json` | [  ] 
| Linux   | `~/.config/OBSMarkers/config.json`                     | [  ]

Example:

```json
{
  "obs": {
    "host": "localhost",
    "port": 4455,
    "password": null
  },
  "markers": {
    "last_folder": "C:/Users/<user>/Videos/Markers"
  },
  "hotkeys": {
    "new_file": "F12",
    "add_marker": "F8"
  }
}
```

## Building the Executable

A PyInstaller spec file is included for reproducible builds.

```bash
pip install pyinstaller
pyinstaller obs-markers.spec
```

The resulting executable will be placed in the `dist/` directory.


## Platform Support

* **Windows**: Fully supported and tested
* **macOS / Linux**: May work when run from source, but not officially supported yet

## Contributing

Contributions are welcome.

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Open a Pull Request


## License

MIT License
© 2025 Jordan “sloth” Mock
