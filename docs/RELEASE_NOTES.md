# Guoran Clock v2.3.1

First public Windows release of the XGGF/IN12_M4 Bluetooth LE desktop controller.

- English and Russian interfaces; persistent light/dark themes.
- Backlight, remote buttons, time, alarms and coordinated schedule editing.
- Menu reference beside the remote and a beginner guide with left/right display examples.
- SET sends Back, then SET after a short pause.
- Received settings and unconfirmed writes are shown separately.

## Downloads

- `GuoranClock-2.3.1-windows-x64.zip`: executable, English user guide and README.
- `GuoranClock-2.3.1.exe`: standalone application executable.
- `SHA256SUMS.txt`: SHA-256 checksums for both downloads.

Windows 10/11 x64, Bluetooth LE and Microsoft Edge WebView2 Runtime are required. Python installation is not required for the packaged application. Extract the ZIP before running it.

## Verification and limitations

21 automated tests passed. The packaged window, inline menu reference and guide diagram were checked on Windows. Earlier versions connected to the physical clock, read settings and sent controls; the owner confirmed device reactions.

The new Back → SET sequence and schedule write ordering have automated coverage, but their complete physical behavior still needs confirmation. Some firmware fields are undecoded. This is an independent project and is not verified with every XGGF clock. macOS and Linux binaries are not provided in this release.
