# Guoran Clock v2.5.0

- Merges [PR #2](https://github.com/Sallaxer/guoran-clock/pull/2): fixes the clock lag observed after time synchronization. Packets are aligned to second boundaries; stopping continuous sync sends a final isolated time packet after a pause.
- Adds Simplified Chinese (简体中文) alongside Russian and English, including controls, the built-in guide, menu reference, status messages and saved language preference.
- Keeps the Russian remote button labels **Увеличить / Уменьшить**.

## Downloads

- `GuoranClock-2.5.0-windows-x64.zip`: Windows executable and documentation.
- `GuoranClock-2.5.0.exe`: standalone Windows executable.
- `GuoranClock-2.5.0-macos-arm64.zip`: macOS application for Apple Silicon.
- `GuoranClock-2.5.0-linux-x86_64.tar.gz`: Linux executable and documentation.
- `SHA256SUMS.txt`: SHA-256 checksums.

Windows 10/11 requires WebView2. macOS 14+ on Apple Silicon: the application is ad-hoc signed, not notarized. Linux targets Ubuntu 24.04 or compatible x86_64 systems with BlueZ, GTK 3 and WebKitGTK 4.1. Chinese text requires a CJK-capable system font (on Ubuntu: `fonts-noto-cjk`). Python is bundled.

## Verification and limitations

Automated tests cover sync ordering, second boundaries, translation completeness, placeholders and language persistence. Packaged startup checks exercise the Chinese and English interfaces on all three operating systems. The PR author measured about 0.3 seconds of remaining lag on one IN12_M4, down from about 2.3 seconds; camera latency and digit transitions affect that measurement. Other firmware may behave differently. If Bluetooth drops during continuous synchronization, synchronize again after reconnecting. Linux Bluetooth still needs physical-device verification.

The interface language does not change the clock's voice language. That remains a separate setting.
