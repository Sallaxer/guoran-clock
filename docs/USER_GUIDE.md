# User guide

## Connect the clock

Power the IN12_M4 with its specified 5 V supply. Enable Bluetooth on the computer, open the application and select **Connect clock → Find clock**. Choose the clock: its Bluetooth name starts with **XGGF**. Enter its current password (the original default is **210709**) and click **Connect**.

If another application is connected to the clock, disconnect it first. Keep the clock near the computer during setup. **Read settings** requests its settings; if there is no response, the application may reconnect. A settings response does not provide a live menu position.

Use the sidebar to select **English** or **Русский**, and switch between light and dark themes. Both choices are saved locally.

## Backlight and remote

Choose a preset, use the hue slider, or open the custom color picker. Click **Apply color** to send the selection. The displayed reply color and the selected color can differ until a new settings response arrives.

The controller exposes six channels, although IN12_M4 has four tubes. Channel mapping depends on firmware. The three backlight-mode buttons reproduce the original remote's previous, M and next commands.

### Enter the settings menu

Click **SET**. The app opens the menu reference beside the remote and sends **Back**, waits 250 ms, then sends **SET**. This preparation addresses the observed requirement to press Back before SET; it does not toggle power. Physical confirmation of this automatic sequence is still pending.

The **Show menu reference** link opens the same reference without sending commands. Hiding it does not exit the menu on the clock.

1. **Select an item on the left.** The left pair of tubes is highlighted. Use **+ / −** to select the code in the table's **Left: menu item** column.
2. **Press OK to select its value on the right.** Highlighting moves to the right pair. Use **+ / −** to select a value from **Right: value**.
3. **Press OK to confirm.** Some items continue into further setup, such as alarm time. Use **Back** to return one level; from the main menu it exits settings.

Example: `02` on the left is **Alarm 1**. After OK, `0` on the right means **off**. Selecting `1` enables the alarm and proceeds to time setup. Watch the highlighted pair and follow the clock's voice prompts.

| Left: menu item | Function | Right: value |
| --- | --- | --- |
| 01 | Time setting | 0: manual; 1: Bluetooth synchronization |
| 02 / 03 | Alarm 1 / Alarm 2 | 0: off; 1: on and set alarm time |
| 04 | Digit transitions | 0–3: transition effects |
| 05 | Colon | 0: off; 1: on |
| 06 | Brightness | 0: automatic; 1: manual adjustment, 10 levels |
| 07 | Volume | 0–7; 0 is silent |
| 08 | Display mode | 1: hours/minutes/seconds; 2: hours/minutes/weekday; 3: month/day/weekday; 4: custom |
| 09 | Time format | 12 or 24 hours |
| 10 | Schedule | 1: turn-on time; 2: turn-off time |
| 11 | Hourly announcement | 0: off; 1: on |
| 12 | Night mode | 0: off; 1: suppress announcements below brightness level 2 |
| 13 | Alarm sound | 1–6 |
| 14 | Weekday backlight colors | 0: off; 1: on; manual color changes are unavailable when enabled |
| 15 | External switch | 0 / 1: reserved interface for external devices |
| 16 | Tube protection | 0: disabled; 5–15: interval in minutes; 5 recommended |
| 17 | Voice language | 0: Chinese; 1: English |
| 18 | Reset | 00: keep settings; 11: restore factory settings |

## Tube protection

The clock periodically cycles through all digits as part of tube protection. This is normal operation. To set the interval, press **SET**, select **16** on the left and press **OK**. Select **5** on the right for the recommended five-minute interval and confirm with **OK**. The manual allows 5–15 minutes; 0 disables protection, which the manufacturer does not recommend.

The **Ambient light sensing** switch is not a verified tube-protection control. Its precise effect on this model is unknown. Use menu item 16 for protection and **Automatic brightness** for brightness adjustment. The sensor type and activation conditions of **Sensor-controlled switching** are also unspecified for this model.

## Time and alarms

Use the time section to send the computer's date and time. Continuous time synchronization is a separate option and stops when the application disconnects or reconnects. The displayed computer time is not a live reading from the clock.

For each alarm, enter the time and click **Set**, then use its on/off switch. Clock menu items 02 and 03 provide the corresponding controls on the device.

## Automatic on/off schedule

Edit **Turn on at** and **Turn off at**. Changes are saved locally, including while disconnected. Enabling the schedule sends both times first, followed by the enable command. If it is already enabled, click **Apply schedule** to send the edited interval. Disabling sends only the disable command.

The three writes are sequential, not an atomic transaction. If a write fails, subsequent commands stop; an earlier time may already have changed. Check the device behavior after applying an important schedule. A **Sent, not confirmed** label is not proof of firmware acceptance.

## Buttons on the case

- **L:** toggle backlight; increase a value in the menu.
- **OK:** toggle clock power; confirm a menu choice.
- **R:** display date; decrease a value in the menu.
- **L + R:** enter or exit settings.
- **OK + R:** timer.

## Troubleshooting

- **Clock not found:** confirm power, Bluetooth and proximity; close another app's connection and scan again.
- **Password rejected:** use the current clock password, not necessarily the original default. This app does not change the password automatically.
- **SET appears ineffective:** the app already sends Back before SET. Observe the clock; the timing of this workaround has not yet been verified on hardware. You can use Back and SET manually as well.
- **Read settings has no reply:** some firmware replies only after authorization. The app reconnects on a read timeout. Avoid interpreting old snapshots as confirmation of a new setting.
- **Unexpected sensor value or invalid time:** the raw field may not match the known protocol. Other settings remain usable.
- **Cannot save a log:** extract the application to a writable folder. Review the exported log for nearby device identifiers before publishing it.

## Power and care

The supplied IN12_M4 manual specifies DC 5 V, current below 400 mA and dimensions of 132 × 50 × 50 mm. Keep the clock dry, avoid strain on its USB connector and do not open the case.
