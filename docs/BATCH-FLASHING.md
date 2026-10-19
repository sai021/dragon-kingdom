# Flashing a batch of Dragon Kingdom boards

On the completed enclosure, the bottom USB-C port is power only. Flashing is a
maker/service operation requiring access to the internal ESP32 USB connector,
which is not accessible to normal users. Disconnect the external product supply
before connecting laptop USB; never connect both powered inputs together.


The [19 October repair checkpoint](RELIABILITY-FIXES-2026-10-19.md) records
the current verified paired S3/C3 bundles, checksums and remaining live tests.
The earlier [18 October checkpoint](RELEASE-CHECKPOINT-2026-10-18.md) is historical.
Use the displayed saved release when programming the repair images; rebuild
after firmware, web or catalog changes. Manual/PDF edits do not change firmware
behaviour and do not require reflashing.

Double-click `dragon-firmware/Flash Dragons.cmd` on Windows, or run
`python tools/batch_flash.py` from `dragon-firmware`. Requires Python with
Tkinter and the Arduino CLI toolchain described in DEVELOPMENT.md. The tool
also finds this project's local `.tools/arduino-cli/arduino-cli.exe`.
Use `--cli PATH` if your CLI is elsewhere.

1. Disconnect external/main power. Use laptop USB only, with a data USB cable.
2. The last successful firmware build for each chip type is loaded when the
   window opens. Click **Build firmware** to build both S3 and C3 from current
   sources. S3 retains its existing 4 MB flash/2 MB PSRAM settings; C3 uses
   4 MB flash, DIO and no PSRAM. Both use the same custom partitions.
   If both saved images are already listed, skip Build and go straight to Flash.
   Builds show compiler output, the current target, elapsed time and an animated
   activity bar (not a completion percentage). The first build can take several
   minutes. Later builds reuse `work-s3`/`work-c3` compiler files; successful
   images are copied into separate immutable bundles before publication. Only
   one updated flasher can build at a time. The displayed log is bounded to keep
   the window responsive; full output remains in the session's `uploader.log`.
3. Connect one ESP32-S3 or ESP32-C3 SuperMini. Close serial monitors. Its port
   is selected automatically; click **Flash this ESP32**. The flasher resets
   the selected board into its ROM loader and reads the chip identity with
   esptool, then uploads the matching saved firmware. Unsupported/unidentified
   chips and missing/corrupt builds stop before any write. There is no checkbox.
4. If it cannot connect, hold **BOOT**, press and release **RESET**, then
   release **BOOT**. Wait for the port to update because its number can
   change in download mode. Retry flashing.
5. After uploading, the flasher checks serial responses for up to 45 seconds.
   With BOOT released, press **RESET** if it is waiting. Wait for
   **STARTUP PASS**, then unplug. This works with a bare board: no matrix or
   voltage divider is required. A pass requires a ready library, a Dragon Kingdom
   status response and increasing uptime over at least two seconds.
   A reported panic, decreasing uptime or missing computer-USB power ceiling
   fails the check.
   If startup is not confirmed, press Reset and click **Check startup (no flash)**
   to retry without rewriting firmware. Close other serial monitors.
6. Disconnect USB, connect the next board and repeat from step 3.

Ports refresh in the background approximately every two seconds while idle.
A single available port or a single newly appearing port is selected
automatically. If several ports appear together, choose the board's port
manually. The dropdown and **Refresh ports** button remain available.
Automatic port selection is separate from chip detection, which happens when
you click Flash. USB port descriptions are not used to infer the chip type.
The power reminder remains visible without requiring a checkbox.

The upload and startup-pass counters count operations, including repeats on
the same board; they do not count unique devices. A startup pass confirms
brief firmware execution, not LED, sensor, power-supply or Wi-Fi operation. The tool
does not automatically flash newly connected devices. Check the selected port
for every board. It supports only the project's S3 and C3 configurations.
Chip detection does not identify a SuperMini PCB revision or check its wiring.

The saved builds, their selection manifests and per-session logs are under ignored
`.tools/batch-flash/`. The manifest stores the board configuration and SHA-256
checksums, checked at launch and before upload. All boards receive those files
until you explicitly build again, even after closing/reopening the program or
restarting the computer. Source edits do not automatically rebuild the firmware.
Each target rebuild stages a new immutable bundle. Both targets must validate
before one atomic `current-set.json` publishes the pair and its source hash.
Failure of either target preserves the complete previous release set; separate
legacy selections are still readable until the first complete paired build. Another normal development build cannot change this batch's files.
The uploader writes the firmware using Arduino CLI's upload recipe; there is
no whole-chip erase option. Existing Wi-Fi settings, profiles and creations
are intended to remain available through the firmware's normal migration.

For a new device's private setup card, use the existing
`tools/capture_web_setup.py --port YOUR_PORT` after flashing/reset, as described
in DEVELOPMENT.md. Cards are a separate step in this first version. Uploader
logs remain inside the ignored batch directory.

Startup checks need `pyserial` (`python -m pip install pyserial`). The flasher
also supports the existing local `.tools/python-packages` installation.
Startup logs contain only the expected status fields, not boot credentials.

Button sequence reference:
[Espressif ESP32-S3 boot mode selection](https://docs.espressif.com/projects/esptool/en/latest/esp32s3/advanced-topics/boot-mode-selection.html).
The upload reuses compiled binaries through
[Arduino CLI's input directory option](https://docs.arduino.cc/arduino-cli/commands-reference/arduino-cli_upload).

Software checks and physical flashing evidence must be recorded separately.
No board is flashed by merely opening this window.

## C3 carrier compatibility

The C3 build assumes the eight power-side header positions shown in the supplied
pinouts: 5V, GND, 3V3, GPIO4 (unused), GPIO3 (matrix), GPIO2 (TTP223),
GPIO1 (voltage divider), GPIO0 (LDR). Check actual board orientation, header
spacing and carrier fit before inserting it. A chip-ID match cannot check these.
GPIO2 is a C3 strapping pin: verify cold starts with touch idle and held,
including the setup gesture. Verify ADC readings against a meter, matrix
operation, Wi-Fi, saves and USB limiting on actual C3 hardware before deployment.
The external TTP223 is required; the C3 has no native capacitive-touch peripheral.
