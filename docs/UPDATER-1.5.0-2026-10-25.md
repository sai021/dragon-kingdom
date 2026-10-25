# Easy Update 1.5.0: automatic USB updates

The owner requested USB alongside the existing Wi-Fi modes, then clarified that
automatic update mode should remain the original workflow. Default AP mode is
unchanged. In USB cable mode, acknowledge external/main power is disconnected
for every board in the batch, then enable Auto update USB dragons. Signed USB
files are prepared before arming. Connect one board, wait for the result, unplug
and wait for Auto ready before the next. Equal firmware is checked without
rewriting; newer firmware is skipped without reset or downgrade. Stop finishes
any current operation. Errors stop Auto for review. Manual port selection remains
available for bridges; native USB Auto filters VID 303A and requires one candidate.

## Shared USB service and preservation

prepare_usb_service.py copies the reviewed recovery, flash_support, board_targets,
release_contract and recovery_batch implementations from dragon-firmware/tools.
Only relative imports, public-key lookup, private application-data root and hidden
Windows process creation flags are adapted. Signature/schema/partition/image gates,
NVS flash ranges/readback and startup checks remain unchanged. The generated sources
are included in the downloaded build recipe. No Arduino CLI or Python installation
is needed on a family computer.

The USB ZIP is fetched over the same restricted HTTPS release hosts. Only exact
manifest/two-board image names (and optional README) are accepted, with bounded
sizes and duplicate/path rejection. Both boards' signed hashes, image chip IDs,
appended image digest and two-slot unchanged-NVS layout are checked before atomic
publication. The manifest must exactly match the selected signed stable release.
Complete per-tag caches are reused offline; invalid caches fail closed. Startup's
Wi-Fi preparation remains; USB Auto/Download USB files prepares the extra USB set.
A USB-only prior cache can be loaded without a Wi-Fi package cache.

Native port enumeration never opens or resets a board. Actual update requires
power confirmation and a current port. The existing runtime source-schema check
runs before ROM/flash operations; unknown or unresponsive source runtime is not
silently treated as safe. NVS is backed up before writing; only bootloader, table,
OTA metadata and app0 ranges are written. No erase-all or NVS write. Readback must
match. Startup checks expected tag/board/app digest, VALID OTA state, ready library,
increasing uptime and 400mA USB report. Private NVS files are under application-data
USB Service/.tools/recovery; their parent is created mode 0700 on POSIX systems.

The standalone unmodified esptool 5.6.0 helper is a separate CLI process under
USB Tools, with exact upstream source/licences and rebuild recipe supplied. The GUI
does not import esptool. Its dependencies and S3/C3 stub resources are included.
Keep USB Tools beside the executable (Windows) or app (Mac).

## Evidence and limits

Source/tag target: 8710b343059feadd1383a054190f1907330f3915.
CI: https://github.com/sai021/dragon-kingdom/actions/runs/40194074294
Fifty-four tests cover signed USB download/offline reload, tamper/path rejection,
power/current-port gates, newer-version skip, delegation to reviewed service,
USB Auto opt-in and once-per-unplug behavior, plus existing AP/HTTP/signature tests.
The generated recovery gate uses the existing reviewed BatchGate implementation.

A source-built Windows package using the Codex runtime failed its SSL smoke with
that runtime's frozen OpenSSL. It is not distributed. The official Python CI-built
Windows ZIP passed self-test and signed Wi-Fi+USB download/reload on this PC, and
its separate helper --help passed without opening a device. The downloaded archive
contains exact esptool/esp-pylib sources and both board stub resources.
No physical USB firmware write was performed; Mac USB writes and actual USB
re-enumeration remain physically unverified. Existing source service tests are
separate from field acceptance. Windows is unsigned; Mac remains ad-hoc signed,
not Apple notarized. Firmware remains stable 0.3.1 and app releases are non-latest.

Manual edition 1.5 includes USB Auto and the exact backplate/power sequence. It
remains ten pages; the one-A4 class sheet now distinguishes Wi-Fi from USB service.
All pages were rendered and visually inspected, and all three QR links decode
unchanged. The existing public guide/manual/notice URLs are retained.

All three CI jobs passed: Windows x64, Apple Silicon Mac and Intel Mac. Downloaded
Mac archives have executable USB helpers, both board stub resources, required
network/location plist descriptions and version 1.5.0. All five uploaded assets
were downloaded and compared byte-for-byte before publication. Release
updater-v1.5.0 is public with latest=false; latest remains firmware v0.3.1.
The guide and both PDFs were pushed to gh-pages at 0f5a01a.
Unauthenticated public downloads match all three archive hashes; both live PDFs
match final local bytes and the live guide shows all three 1.5.0 download links.
