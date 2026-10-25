# Dragon Kingdom Easy Update

Version 1.4.0 checks the signed latest stable release at startup and automatically
prepares all four board/bridge packages if they are not already cached. A failed
refresh preserves the complete verified saved release and clearly labels it as
potentially stale. Startup never scans, switches Wi-Fi or installs firmware.

Find & update all dragons is the explicit direct-mode installation action. It
scans Dragon setup networks once, deduplicates SSIDs, then joins each sequentially,
checks HTTP identity against the SSID and updates only older firmware. Current
and newer firmware are skipped without login or flash. Each update retains the
signed package/backup/startup/settings checks. Per-lamp failures are reported and
the next lamp is attempted only after returning to original Wi-Fi. A restoration
failure stops the batch. Stop aborts safely before finalization; after finalization
it lets verification finish and skips remaining lamps. A scrollable results report
includes each outcome and backup path. No automatic retries of uncertain finishes.
Use the bulk action only where all nearby dragon APs are yours to update.

Parent password dragon123 remains prefilled, editable and memory-only. Home Wi-Fi
and manual direct connection retain individual Update selected dragon. Neither
opening the app nor merely connecting manually installs firmware.

Direct mode refuses to start a firmware write if the lamp reports home Wi-Fi
connected: beta 3 and current firmware close their AP 15 seconds after joining
home Wi-Fi regardless of attached clients. Use Home Wi-Fi mode for those lamps.
Direct mode is for unconfigured lamps or those unable to join their saved network.

Windows uses Native Wi-Fi and an in-memory temporary WPA2 profile; it does not
save/replace connection profiles or read the home password. Mac uses CoreWLAN,
with CoreLocation consent, and asks the OS to restore the saved original network.
Wi-Fi/location access can be denied by OS or managed-computer policy. No privacy
settings are changed by the app. Original network details remain in RAM only.
Mac return is best effort without extracting keychain passwords; manual return
may be necessary. Direct-mode restart validation allows up to five minutes.

Download for offline use verifies and atomically stores both board types and
both ordinary/legacy packages in the user's application-data Firmware folder.
The signed cache survives app restart; every offline load revalidates all files,
and offline package selection never falls back to internet. Partial downloads
leave the previous complete cache intact. Re-run the download step on internet
to prepare a later release. No firmware is installed by downloading/preparing.

Windows and Mac application for deliberate, signed firmware updates over the
local home network. No USB, firmware bundled into the app, home Wi-Fi password input,
startup installation, factory reset or cloud backup. The same application fetches
later main firmware releases. The firmware release must remain GitHub's latest;
publish application releases with `--latest=false`.

Run `python -m pip install -r requirements.txt`, then `python main.py`.
`python -m unittest discover -s tests -v` exercises both boards and both wire
formats with real local HTTP fake lamps, including dropped replies, cancellation,
rollback and settings mismatch. These are simulations, not physical acceptance.
`python main.py --self-test` checks the GUI and bundled public trust root without
network discovery or writes. `python package.py` builds and self-tests on Windows
or Mac; the workflow produces separate Windows x64, Mac arm64 and Mac x86_64 ZIPs.
The app is not Windows certificate-signed or Apple Developer ID notarized. Mac
bundles have ad-hoc signing. Do not describe them as OS-trusted signed apps.
Packages include dependency licence notices, unmodified Zeroconf LGPL source,
and this updater's source/build recipe. You may rebuild the updater with modified
LGPL libraries. Install pinned requirements in a fresh Python 3.12 environment,
replace the desired library there, and run package.py on the target OS. On Intel
Mac build cryptography with OPENSSL_STATIC=1 to avoid bundled libssl collisions.

Discovery uses mDNS and at most two active local IPv4 /24 ranges (512 addresses,
24 workers); Add address handles other subnet layouts. Guest isolation and VPNs
can prevent discovery. Lamp requests bypass proxies and refuse redirects; only
private IPv4 HTTP port 80 is accepted. Parent passwords/tokens are memory-only.
Local HTTP is the existing lamp protocol; use a trusted home network.

Before writing, the app verifies the signed release contract, board, size, image
digest, compatibility contract and RSA signature against the installed firmware
trust root. It refuses downgrade and pre-0.3 single-slot devices. Old 0.3.0 beta
1–3 and 0.3.0 stable use the explicit format-1 bridge to the same calibration-aware
image; later firmware uses format 2. Backup must be saved before START. Uncertain
chunk acknowledgements are checked by offset before retrying (beta 3 rejects
duplicates). Cancellation aborts before finalization. After finalization the app
waits for validated startup and compares persistent backup fields, excluding
volatile phone time/timezone rules and CRC. No automatic backup restore.

Backups contain personal settings and stay in the OS user's private application
data folder. Keep private. Physical lighting/touch/power checks remain necessary.
