# USB production recovery and first migration

![USB recovery power sequence](images/usb-recovery.svg)

Never connect laptop USB and external/main power simultaneously. The bottom USB-C
port is power-only. Confirm the current identity and port on every board.

## Open the backplate

1. Disconnect the bottom product USB-C power cable before connecting laptop USB.
2. Remove the screw at the top rear of the box.
3. Using a screwdriver through the rear keyhole, push the release tab until the backplate pops open.
4. Connect the laptop USB-C cable to the ESP32 on the main board in the centre of the backplate.

## Easy Update USB Auto

Easy Update 1.7.0 also offers **USB cable** mode for the signed recovery workflow.
Open it on internet, choose USB cable, read the USB-only power warning and optionally
enable Auto update USB dragons. It prepares the signed bundle before arming.
Connect one ESP32 at a time, wait for the result, unplug and wait for Auto ready
before the next. Equal firmware is checked without writing; newer firmware is
skipped. Stop finishes any current operation. Errors stop Auto for review. USB
re-enumeration cannot trigger a second update. Keep the whole ZIP extraction,
including USB Tools. Manual port selection and the original service tools remain.

The installation path is detected automatically. Known compatible Dragon firmware
is backed up and updated. Unknown firmware or an unavailable backup offers only
Abort or Continue without backup. Continue replaces existing firmware/saved data
when the installed format is unknown; a raw snapshot is not a compatible Dragon
settings backup. There are no Update/Fresh installation radio buttons.

Both Wi-Fi and USB files prepare automatically at startup with internet. Offline,
use verified saved files or Choose firmware file… to import the signed complete
firmware ZIP from the PC. The family guide links that file for copying from another
computer. It is not the updater application ZIP.

## Restore firmware


1. Confirm external/product power remains disconnected and laptop USB is connected only to the internal ESP32.
2. Open `Flash Dragons.cmd` or `Recover Dragon.cmd`. Both use the same workflow.
3. Choose **Select signed release bundle** and explicitly select an immutable
   format-2 release directory prepared by `tools/prepare_release.py`. Old unsigned
   recovery sets are rejected. Check the displayed expected tag and both-board
   hash/layout verification. No source rebuild is performed by the production GUI.
4. Ports are discovered at launch and refreshed automatically while idle, even
   before selecting a release bundle. A single/newly connected port is selected
   automatically; **Refresh ports** also retries discovery. Select the current
   board and confirm USB-only power. Changing the selected port clears that
   confirmation; discovery alone never starts recovery.
5. Choose **Update / recover firmware**. ROM identification chooses the correct
   board. Signed compatibility, hashes and partition layout are checked before any
   write. NVS is privately backed up; only bootloader, partition table, OTA metadata
   and app0 are written. Whole-flash erase is never used.
6. NVS must read back unchanged. After reset the expected firmware/board/running-image digest, increasing
   uptime, ready library, 400 mA USB estimate and VALID application are required.
   Missing version/validation, rollback to another tag, or zero-budget bare-board
   startup cannot receive a production pass. Check saved contents separately.
7. After restoring firmware, disconnect laptop USB. Fit the backplate's bottom USB-C port and LDR (room-light sensor) into their respective slots in the box. Press the top of the backplate until it pops into place, then replace the screw. Reconnect normal product power only after laptop USB is disconnected. Complete and record
   LED/touch/LDR/external-power and other [physical checks](PHYSICAL-ACCEPTANCE.md).

Auto mode requires one board at a time and explicit USB-only acknowledgement.
Older/legacy firmware can update to the selected compatible release; an equal
version is checked without writing. A newer version is refused so it cannot be
mistaken for the selected production release. Confirm unplugging before the next
board; USB re-enumeration alone must never initiate another flash.

CLI:

    python dragon-firmware/tools/recovery.py --bundle IMMUTABLE_RELEASE_DIRECTORY --port CURRENT_PORT --usb-only --esptool FULL_PATH_TO_ESPTOOL

Install `requirements-service.txt` for USB tools. Use the pinned standalone esptool
or Arduino-installed tool. Do not disable host protections if a tool is blocked.
Current tools support the existing schema-1 installed releases; future/custom saved
schemas require a separately reviewed migration. A corrupt restore journal has
its own [evidence-preserving service path](RESTORE-SERVICE.md).

These are tool contracts, not new physical evidence. S3/C3 candidate migration,
rollback and power tests remain pending. Keep all NVS files and unit identifiers
under ignored local output; they may contain household credentials.


USB source-schema gate: runtime now reports its saved-data schema. Recovery refuses
unknown or mismatched source schemas before any write. Known stable 0.3.0/beta 1-3
use the historical schema-1 contract. For an unbootable or unreported legacy image,
first retain a verified private raw NVS dump with `restore_service.py`, review its
original firmware/schema, then deliberately supply `--source-schema 1` to CLI recovery.
This service assertion is never inferred by Auto mode and does not bypass signed
target compatibility. A future schema needs a separate migration, not this assertion.
