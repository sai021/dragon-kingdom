# Unreleased Easy Update workshop preview - 26 October 2026

The owner reported USB schema rejection, requested support for empty boards,
asked for a Dragon Kingdom redesign before another version, and explicitly asked
for a way to replace firmware on boards previously used for other projects.

The current COM17 board was read through serial status after current USB-only
power confirmation. It emits uptime/current-cap lines but no firmware/schema
metadata. This is an old/unidentified runtime, not a proven blank board. No ROM
flash operation was performed against it; no data was erased or firmware written.
Preservation must not silently override that missing source contract.

The view is now separated into workshop_ui.py. Forest green, warm parchment,
gold accents, Georgia/Segoe UI type, an original 8x8 LED crest and three connection
cards replace the generic utility presentation. The USB area exposes the two
installation policies. Selecting Fresh install is sufficient to select replacement;
there is no second acknowledgement. USB power is a visible warning, with no
checkbox. Auto mode is optional. Non-applicable address controls and parent password are
hidden. Full progress details remain in a scrollable activity log. Native view
inspection used the computer-use skill and a separate explicitly marked design
preview whose hardware actions are disabled. The preview must not be mistaken
for a physical acceptance test.

Update and keep saved dragons remains default. On absent version/runtime, the USB
adapter can inspect for an entirely erased board; non-empty contents are preserved
and the error directs the user to the explicit Fresh install option. Fresh install
uses the selected replacement policy and requires USB-only power. It validates
the signed stable bundle before ROM access, identifies S3/C3 and a supported
4/8/16MB flash, automatically saves two full raw reads and checks equal size/hash.
If that fails, the user gets exactly Abort or Continue without backup. Abort stops
before erasing/writing. Continue explicitly permits installation without a verified
backup, records that decision and does not claim that saved data was verified.
Those private backups can contain credentials. A non-empty board is erased only
with replacement=True; a fully erased board needs no erase command. Both install
the signed bootloader/table/OTA/application, check erased NVS before first boot
when flash reads are available,
then verify the expected firmware/image/board, VALID startup and USB ceiling.
Failure attempts to return the chip from ROM to runtime without writing firmware.
The preservation path keeps schema and layout gates and excludes NVS from write
ranges. Failed NVS backup offers the same Abort/Continue decision; Continue skips
unavailable NVS verification and reports that limitation explicitly.

This does not claim that a full backup is an automatic restore mechanism. Do not
use private flash dumps as general firmware images; retain for maker-assisted
recovery. There is no schema guess or bypass in update mode. Fresh install means
new saved data after explicit replacement, not a migration of unknown data.

Validation: desktop tests cover replacement selection without additional
acknowledgements, the two-button backup prompt, absent-runtime
classification without implicit erase, Auto opt-in and unplug latching. Eight
service tests use real temporary backup files and a simulated flasher, covering
empty initialization, used-board rejection, two-read verification before erase,
backup-failure Abort/Continue, bad flash size/NVS refusal and the power gate. Existing recovery tests
remain separate. The owner then asked to complete the task. Version 1.6.0 is being packaged for
Windows and both Mac architectures; publication evidence will be recorded below.
