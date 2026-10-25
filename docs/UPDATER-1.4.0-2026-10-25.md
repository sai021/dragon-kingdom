# Easy Update 1.4.0: startup firmware download and AP batch updates

The owner requested automatic latest stable firmware download at launch and one
button to find/update all AP-mode lamps that are behind the stable version.

Startup runs on a worker, loads and verifies the complete cache, checks the signed
main-release pointer and prepares all four board/bridge packages when needed.
An unchanged complete current set is reused. A failed check/download retains the
prior verified set and explicitly says it may not be newest. No saved release
means updates require a successful internet download first. Startup never scans,
changes Wi-Fi or installs firmware. Existing atomic offline publication is kept.

Find & update all dragons explicitly authorizes the batch. It scans once,
deduplicates SSIDs, joins sequentially, checks HTTP identity against each SSID,
compares versions and updates only older firmware through the existing verified
core. Current/newer lamps are skipped without flash or downgrade. Each update
keeps the backup, signature/board/contract and startup/settings checks. No replay
of ambiguous finishes is added. Each result includes status, details and backup
path in a scrollable report; live rows show the latest observed firmware.

Failures can continue after restoration to the original network. Restoration
failure stops the batch before another connection; remaining lamps are explicitly
not attempted. Stop cancels before finalization, or lets the current finalization
and restart checks finish and skips all remaining lamps. Password is prefilled,
editable and memory-only. Home Wi-Fi and manual connection retain individual
installation. Batch use is for environments where all nearby dragons are the
user's to update. Home-connected lamps still require Home Wi-Fi mode because
beta 3/current AP handover closes 15 seconds after a saved-home join.

## Validation

Source/tag target: a75a42ff265e8b199ac548fa283f2e8b3d0ee0f4.
CI: https://github.com/sai021/dragon-kingdom/actions/runs/40190948107
Forty-six tests cover startup/no installation, cache reuse, offline and interrupted
refresh fallback, mixed S3/C3 batches, deduplication, no downgrade, wrong lamp,
continuation after error, restoration failure, stop before/after finalization,
GUI result rows and existing simulated HTTP/signature/cache/native API cases.
Tk test objects are collected on the main thread before HTTP test workers start.

No physical batch firmware write or new radio association test was performed for
this change. Prior Windows association/read/return evidence is separate. Mac
association and post-reboot radio handover remain physically unverified. Windows
is unsigned; Mac apps are ad-hoc signed and not Apple notarized. Manual and phone
alternatives remain. Firmware stays 0.3.1; app publication must be non-latest.

Manual edition 1.4 and the class notice explain startup download, one-button batch,
current/newer skips, results and the Home Wi-Fi alternative. Printed URLs remain.

All three CI package jobs passed (Windows x64, Mac arm64, Mac Intel). The downloaded
Windows archive passed GUI/native-binding launch and real signed HTTPS/offline
reload checks on this PC. Archive inspection checked all three packages' public
key, CA bundle, dependency source and matching batch_update.py source. Both built
Mac plists have version 1.4.0 and network/location usage descriptions. All five
uploaded assets were downloaded and byte-compared before publication.

Release updater-v1.4.0 is public with latest=false; latest still points to v0.3.1.
Guide/manual/notice were pushed to gh-pages at 7daa4a3. Manual edition 1.4 remains
ten pages, the class notice one A4 page; all pages were rendered and visually
checked and all three notice QR destinations decoded unchanged.
Unauthenticated public downloads matched all three archive hashes; the live guide
shows 1.4.0 download buttons and both public PDFs match local final bytes.
