# Guoran Clock

A desktop controller (Windows, macOS, Linux) for XGGF Bluetooth LE nixie clocks, developed with an IN12_M4 clock with four IN-12 tubes. It replaces the basic controls of the older Guoran Android application with a desktop interface.

<p align="center"><img src="ui/clock-ui.png" alt="Four-tube IN12_M4 clock in a wooden case" width="520"></p>

**[Download the latest release](https://github.com/Sallaxer/guoran-clock/releases/latest)** · **[User guide](docs/USER_GUIDE.md)** · **[Bluetooth protocol](docs/PROTOCOL.md)**

## Features

- Bluetooth LE discovery, connection and settings readback.
- Backlight color, available controller channels and remote-control buttons.
- Time synchronization, two alarms and an on/off schedule.
- A menu reference beside the remote, opened automatically by SET.
- English and Russian interfaces, light and dark themes.
- Local preferences and exportable diagnostic logs; no cloud service.

## Requirements

- Windows 10 or 11 with Microsoft Edge WebView2 Runtime, macOS 12 or later, or Linux with BlueZ and WebKitGTK.
- A working Bluetooth LE adapter.
- A compatible XGGF clock. Compatibility with every model or firmware is not established.

The packaged application does not require a separate Python installation. Windows and macOS builds have been used with the physical clock. Linux support is untested with hardware: the tests, window start-up and packaging were checked in a Debian container without a Bluetooth adapter.

On macOS the first scan asks for Bluetooth access; allow it in the dialog or later in System Settings → Privacy & Security → Bluetooth. macOS cannot turn the Bluetooth radio on for an app, so **Enable Bluetooth** opens the Bluetooth settings instead. On Linux the button powers the adapter through BlueZ; an rfkill block must be removed separately.

## Quick start

1. Download the package for your system from Releases: `GuoranClock-2.3.1-windows-x64.zip` (extract to a writable folder), `GuoranClock-2.3.1-macos-arm64.zip` (move `GuoranClock.app` to Applications) or the Linux binary.
2. Power on the clock, enable Bluetooth on the computer and run the application. The macOS build is ad-hoc signed, not notarized: open it the first time with right-click → **Open**.
3. Choose **Connect clock → Find clock**. Select a device whose name starts with **XGGF**.
4. Enter the clock's current six-digit password. The original app's default is **210709**. Click **Connect**.
5. Select **English** in the sidebar if needed. Choose a backlight color and click **Apply color**.

Close another app's clock connection before connecting from this application. Read the [user guide](docs/USER_GUIDE.md) for SET/OK navigation, schedules and tube protection.

## Understanding device feedback

**Clock reply** means the value came from a settings response. **Sent, not confirmed** means Bluetooth accepted the write, but the clock has not confirmed that setting in a new response. A successful Bluetooth write alone does not prove that the firmware applied it.

Some firmware returns unusual sensor values or invalid schedule times. Those fields remain unknown without hiding other settings. Read settings requests a new snapshot and may reconnect if the clock does not reply. The snapshot is not a live view of the clock's menu or current time.

SET sends **Back → 250 ms pause → SET**, based on observed behavior of the tested clock. This sequence is covered by automated transport tests; its physical effect still needs confirmation. Uncertain sensor functions are identified in the interface rather than given an invented meaning.

## Build from source

Windows, Python 3.13 x64:

```powershell
python -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
.venv/Scripts/python.exe -m unittest discover -s tests -v
.venv/Scripts/python.exe guoran_desktop.py
./scripts/build.ps1 -Python "$PWD/.venv/Scripts/python.exe"
```

The build script runs the tests and creates `releases/GuoranClock-2.3.1.exe`. The Windows package includes Python and application dependencies. The system WebView2 runtime is still required.

macOS, Python 3.13 or later (for example from Homebrew):

```sh
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
PYTHON=.venv/bin/python ./scripts/build.sh
open releases/GuoranClock.app
```

`build.sh` adds the Bluetooth usage description to `Info.plist`, signs the bundle ad hoc and creates `releases/GuoranClock-2.3.1-macos-<arch>.zip` for the build machine's architecture. Run the app from the bundle: a plain `python guoran_desktop.py` from a terminal is killed by macOS on the first Bluetooth call unless the terminal application itself has Bluetooth access.

Linux (Debian/Ubuntu package names), using the system GTK bindings:

```sh
sudo apt install python3-venv libpython3-dev python3-gi gir1.2-webkit2-4.1 bluez
python3 -m venv --system-site-packages .venv
.venv/bin/pip install -r requirements.txt
.venv/bin/python guoran_desktop.py
PYTHON=.venv/bin/python ./scripts/build.sh
```

The Linux build creates a single-file `releases/GuoranClock-2.3.1-linux-<arch>`. It still uses the system WebKitGTK libraries.

## Project layout

| Path | Purpose |
| --- | --- |
| `guoran_desktop.py` | Window API, application state and preferences |
| `bluetooth_backend.py` | BLE worker, authentication, writes and notifications |
| `protocol.py` | Command formatting and response parsing |
| `localization.py` | Backend status translations |
| `ui/` | HTML/CSS/JavaScript interface and clock artwork |
| `tests/` | Protocol, transport, state and command-sequence tests |
| `scripts/build.ps1` | Windows build script |
| `scripts/build.sh` | macOS and Linux build script |
| `docs/` | User guide, protocol and release notes |

Preferences are stored in `%LOCALAPPDATA%/GuoranClock/preferences.json` on Windows, `~/Library/Application Support/GuoranClock/preferences.json` on macOS and `~/.config/GuoranClock/preferences.json` on Linux. The connection password is not saved there. Exported logs are written beside the executable on Windows, to `~/Library/Logs/GuoranClock/` on macOS (shown in Finder after saving) and to `~/Downloads` on Linux. They may contain nearby Bluetooth device names and addresses; review them before attaching them to a public issue.

The protocol was studied from the original Android app. This is an independent project, not an official manufacturer release. The repository does not include the APK, original manual scans, warranty documents or private diagnostic logs. Clock artwork was generated by editing a photograph supplied by the project owner.

## Original manufacturer resources

The supplied clock manual lists the [manufacturer website](https://diym.vip) and the [original Guoran Android APK](https://diym.vip/upload/guoran.apk). The leaflet also prints [www.diym.vip](https://www.diym.vip). See [Original resources](docs/ORIGINAL_RESOURCES.md) for source details and availability notes.
