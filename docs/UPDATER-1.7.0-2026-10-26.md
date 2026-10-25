# Easy Update 1.7.0: detect firmware and prepare files automatically

The owner found that 1.6.0 still rejected an unidentified board and requested
Fresh install selection. That was the wrong workflow. Version 1.7.0 removes the
installation radio buttons. Known compatible Dragon firmware follows the existing
schema/layout-preserving backup/update path. Unknown firmware or an unavailable
backup offers only Abort or Continue without backup. Abort precedes erase/write.
Continue authorizes replacement of unknown firmware and saved data. A full private
raw flash snapshot can be retained but is not a compatible Dragon settings backup.
Empty boards initialize after empty-flash verification. Signed board/image/layout
and validated startup requirements remain. Physical USB writes are not claimed.

Both Wi-Fi and USB firmware prepare at startup with internet. The two download
buttons are removed. Choose firmware file… imports a complete signed firmware ZIP
from the PC without internet. A USB-only signed recovery ZIP or complete offline
Wi-Fi JSON also works for its transport. Full imports verify both sets before
publication; invalid files do not replace verified caches. Selected USB files take
precedence over another Wi-Fi release in memory, and the selected version appears
when switching modes. A complete firmware ZIP is provided as a separate download
for copying from another computer. The ZIP contains only signed firmware, not
credentials or personal device data. Firmware remains v0.3.1.

Source: e75d86d3dbf6f9e3ee96e2b8eefdb6d9f4cbefec.
Final CI: https://github.com/sai021/dragon-kingdom/actions/runs/40199647309
The earlier candidate run 40199321658 is superseded. Local checks include 65
desktop tests, 9 simulated recovery tests and 24 existing release/batch tests.
The integration test passes an unidentified non-empty board through usb.update
and the actual generated recovery implementation with a simulated flasher,
covering both choices without any installation-policy selection. Local import
tests block internet and check tamper rejection, cache retention, signed contents
and safe archive paths. A real signed v0.3.1 complete firmware ZIP was created
and reimported with downloads blocked. The native preview was visually checked:
no installation choices or download buttons, with optional Auto and local-file
selection. Manual edition 1.7 remains ten pages; changed pages were rendered and
inspected. No firmware was flashed to the attached board. Mac USB hardware
acceptance remains pending. Windows is unsigned; Mac is ad-hoc signed, not notarized.

All three final CI jobs passed. Downloaded Windows final-source GUI/service/TLS
self-test and signed release/download/offline local-file import also passed on the
development PC. All three archives contain the exact final source. Both Mac
archives have version 1.7.0, usage descriptions and executable helpers.

Public release:
https://github.com/sai021/dragon-kingdom/releases/tag/updater-v1.7.0
All six public assets (three app archives, complete firmware ZIP, checksums and
provenance) were downloaded anonymously and matched local hashes. The release is
non-latest; the latest firmware API remains v0.3.1. Pages commit d15f7d0 publishes
the updated guide/manual. The class-sheet bytes and stable QR links are unchanged.

Live guide checks confirm all four 1.7.0 download links, no old download-button
instructions and the simplified choices. Both live PDFs match the local final bytes.
