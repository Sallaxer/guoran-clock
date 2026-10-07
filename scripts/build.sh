#!/bin/sh
# macOS: releases/GuoranClock.app and a zip; Linux: a single-file binary.
set -eu
PYTHON=${PYTHON:-python3}
VERSION=2.4.0
cd "$(dirname "$0")/.."
ROOT=$PWD

"$PYTHON" -m unittest discover -s tests -v

case "$(uname -s)" in
Darwin)
    ARCH=$(uname -m)
    "$PYTHON" -m PyInstaller --noconfirm --windowed --name GuoranClock \
        --osx-bundle-identifier io.github.sallaxer.guoranclock \
        --icon "$ROOT/ui/clock-ui.png" --add-data "$ROOT/ui:ui" \
        --distpath "$ROOT/releases" --workpath "$ROOT/build" --specpath "$ROOT/build" \
        --collect-all bleak "$ROOT/guoran_desktop.py"
    APP="$ROOT/releases/GuoranClock.app"
    PLIST="$APP/Contents/Info.plist"
    # Without this key macOS kills the process on its first CoreBluetooth call.
    plutil -replace NSBluetoothAlwaysUsageDescription -string \
        'Guoran Clock connects to your nixie clock over Bluetooth LE.' "$PLIST"
    plutil -replace CFBundleShortVersionString -string "$VERSION" "$PLIST"
    plutil -replace CFBundleVersion -string "$VERSION" "$PLIST"
    codesign --force --deep --sign - "$APP"
    ZIP="$ROOT/releases/GuoranClock-$VERSION-macos-$ARCH.zip"
    rm -f "$ZIP"
    ditto -c -k --keepParent "$APP" "$ZIP"
    shasum -a 256 "$ZIP"
    ;;
Linux)
    ARCH=$(uname -m)
    "$PYTHON" -m PyInstaller --noconfirm --onefile --windowed --name "GuoranClock-$VERSION-linux-$ARCH" \
        --add-data "$ROOT/ui:ui" \
        --distpath "$ROOT/releases" --workpath "$ROOT/build" --specpath "$ROOT/build" \
        --collect-all bleak "$ROOT/guoran_desktop.py"
    sha256sum "$ROOT/releases/GuoranClock-$VERSION-linux-$ARCH"
    ;;
*)
    echo "Use scripts/build.ps1 on Windows" >&2
    exit 1
    ;;
esac
