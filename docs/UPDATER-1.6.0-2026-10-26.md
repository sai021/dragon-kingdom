# Easy Update 1.6.0: workshop design and simpler USB installation

The owner requested a Dragon Kingdom design, blank/reused-board installation,
and then a simpler flow. The application shows a static USB-only power warning,
with no power or replacement acknowledgement checkbox. Auto is optional.
Selecting Fresh install / reuse this board is the replacement instruction.
Backups run automatically; backup failure offers exactly Abort or Continue
without backup. Abort prevents erasure/writes. Continue records the missing
verified backup and the result does not claim saved-data verification.

Update & keep saved dragons remains default. A supported lamp keeps the existing
schema/layout gates and writes exclude its NVS partition. Proven-empty boards
initialize. Non-empty unidentified boards require Fresh install to replace their
contents. Fresh install verifies signed matching S3/C3 images and 4/8/16MB flash,
tries two full backup reads and verifies size/hash, then writes the signed set
and requires matching image/version/board, VALID startup and the 400mA USB cap.
A user-approved failed-backup continuation skips unavailable readback checks.
No schema is guessed. AP batches, Home Wi-Fi, editable prefilled password and
signed stable firmware preparation remain available. Firmware stays v0.3.1.

Source: 3a2b90385c8e1b845b6b820f3c3f1423d1d95550.
CI run: https://github.com/sai021/dragon-kingdom/actions/runs/40197477518
Local validation: 58 desktop tests, 8 simulated USB installation/backup tests,
15 release-service tests and 9 recovery batch tests pass. Simulated tests check
Abort before writes, Continue behavior, preservation ranges, blank-board
initialization, replacement selection, signed assets and unplug latching.
The official Windows CI package passes GUI/service/TLS self-test, signed Wi-Fi
and USB download/offline-cache reload on the development PC, and helper --help.
The simplified native preview was visually inspected with hardware commands
replaced by inert preview actions. Manual edition 1.6 is ten pages; its changed
service page was rendered and inspected. Class-sheet QR links are unchanged.

Physical evidence remains separate: no USB firmware was written to the attached
unidentified board. Fresh installation and failed-backup continuation have not
been physically exercised. Mac USB hardware acceptance remains pending.
Windows is unsigned; Mac uses ad-hoc signing without Apple notarization.

All three CI jobs succeeded. The public release is
https://github.com/sai021/dragon-kingdom/releases/tag/updater-v1.6.0
with latest=false. All five public assets (three archives, SHA256SUMS.txt and
updater-provenance.json) were downloaded anonymously and matched local hashes.
Both Mac archives contain version 1.6.0 metadata, local-network/location usage
descriptions, executable USB helpers and matching source. The latest firmware
API still returns v0.3.1. Pages commit cb4e6d2 publishes the guide/manual. Live
checks confirm all three new download links and byte-identical manual/class PDFs.
The stable family download address remains
https://sai021.github.io/dragon-kingdom/update/ .
