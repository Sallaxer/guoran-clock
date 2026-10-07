# Guoran Clock v2.4.0

Adds macOS and Linux support from [PR #1](https://github.com/Sallaxer/guoran-clock/pull/1), contributed by aleksei-bochkarev.

- Native packages for Windows x64, macOS Apple Silicon and Linux x86_64.
- Platform-specific preferences, diagnostic log locations and Bluetooth controls.
- macOS Bluetooth permission description and ad-hoc application signing.
- Dark theme by default, with the existing light theme available.
- Remote buttons remain **Increase / Decrease** (**Увеличить / Уменьшить**).
- Automated unit tests and packaged interface startup checks on all three platforms.

## Downloads

- `GuoranClock-2.4.0-windows-x64.zip`: Windows executable and English documentation.
- `GuoranClock-2.4.0.exe`: standalone Windows executable.
- `GuoranClock-2.4.0-macos-arm64.zip`: macOS application bundle for Apple Silicon.
- `GuoranClock-2.4.0-linux-x86_64.tar.gz`: Linux executable and English documentation.
- `SHA256SUMS.txt`: checksums for the downloadable packages.

Python installation is not required. Windows 10/11 requires Microsoft Edge WebView2. The macOS build targets macOS 14+ on Apple Silicon; it is ad-hoc signed, not notarized. Linux is built on Ubuntu 24.04 and requires compatible system libraries, BlueZ, GTK 3 and WebKitGTK 4.1. On Ubuntu install `bluez python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-webkit2-4.1`.

## Verification and limitations

CI checks unit tests and opens each packaged interface, verifies the API bridge, menu table and remote button labels. CI does not exercise Bluetooth hardware. Earlier Windows builds worked with the owner's clock; the PR author reports successful macOS hardware use. Linux Bluetooth operation remains unverified with a physical clock.

Some firmware fields remain undecoded. Successful Bluetooth writes do not by themselves confirm the clock applied a setting. See the user guide for feedback and SET navigation.
