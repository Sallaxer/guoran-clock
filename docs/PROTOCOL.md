# Bluetooth protocol

Observed from the original Guoran Android application's HTML/JavaScript and a tested IN12_M4 clock. This is an implementation reference, not a manufacturer specification. Firmware behavior can differ.

## GATT endpoints

Short UUIDs expand to `0000xxxx-0000-1000-8000-00805f9b34fb`.

| Purpose | Service | Characteristic |
| --- | --- | --- |
| ASCII command writes | FFE5 | FFE9 |
| Settings notifications | FFE0 | FFE4 |
| Authentication write | FFC0 | FFC1 |
| Authentication result | FFC0 | FFC2 |

The app sends the current six-digit password twice as ASCII. With the original default this is `210709210709`. It does not send the Android app's initial-password setup sequence. FFC2 returns a binary status byte: 0 accepted, 1 rejected, 2 changed, 3 removed.

## Commands

Commands are ASCII with no CR/LF suffix. The transport serializes writes and splits long commands as necessary. It prefers writes with response when supported.

| Command | Meaning |
| --- | --- |
| `OSC` | Request settings |
| `Rrrr-Gggg-Bbbb` | RGB components, three decimal digits each, 000–255 |
| `S11`…`S61` / `S10`…`S60` | Channels 1–6 on/off |
| `S71` / `S70` | Time synchronization |
| `S81` / `S80`, `S91` / `S90` | Alarms 1 and 2 |
| `S01` / `S00` | Schedule enabled/disabled |
| `SA1` / `SA0` | Automatic brightness |
| `SB1` / `SB0` | 12-hour format |
| `SC1` / `SC0` | Original label: Ambient light induction; exact device behavior unresolved |
| `SD1` / `SD0` | Hourly voice announcement |
| `SE1` / `SE0` | English voice |
| `SF1` / `SF0` | Original label: Inductive switch; sensor behavior unresolved |
| `AHH:MMA`, `AHH:MMB` | Alarm times |
| `THH:MMO`, `THH:MMC` | Scheduled on/off times |
| `$YYYY-MM-DD;HH:MM:SS;0w` | Date/time; w is weekday, 0 = Sunday |
| `K01`, `K02`, `K03` | Previous backlight mode, M, next mode |
| `K04`, `K05`, `K06` | Power, Back, + |
| `K07`, `K08`, `K09` | SET, OK, − |

## Settings response

A response has 93 ASCII characters: RGB (14), sixteen switch fields (48), four time fields (28), and the `CSS` suffix (3). Switch order is `1,2,3,4,5,6,7,8,9,0,A,B,C,D,E,F`. Time order is alarm 1, alarm 2, on, off. Notifications may fragment the response; the parser reassembles it.

FFE4 supports notifications rather than direct reads on the tested device. Repeated OSC requests can receive no reply. Some responses have nonbinary C values or invalid times such as 44:29. Raw values are retained and only the affected field becomes unknown.

Successful GATT completion confirms transport delivery, not application by firmware. Requested values are tracked separately; matching fields in a subsequent response clear the pending marker.

## Schedule and SET behavior

The original Android app writes each selected schedule time separately and sends S01/S00 on toggle. The desktop app saves a local draft, then sends `THH:MMO` → `THH:MMC` → `S01` as one serialized operation. It stops on error. Disabling sends only S00. The sequence is not atomic.

SET in 2.3.1 sends K05, waits 250 ms, then sends K07. This is based on the owner's observation that SET responds after Back. No power toggle is sent. Automated tests cover ordering and failure behavior; hardware confirmation is still pending.

Manual menu 16 is tube protection: 0 disabled, 5–15 minute interval, 5 recommended. No direct interval-setting command was found. Do not equate SC with menu 16, or SF with the reserved external-switch interface in menu 15, without further device evidence.
