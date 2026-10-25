# Dragon Kingdom Easy Update

Version 1.3.0 names the app Easy Update and starts in offline/direct mode.
The editable parent password is prefilled with dragon123 and stays in memory
for subsequent lamps. Update selected dragon starts the existing backup and
verified installation flow without an extra confirmation dialog. Connecting
still does not install firmware. Native Wi-Fi discovery and connection remain.
Find dragon Wi-Fi downloads the complete signed release first if needed, scans
for WPA2 Dragon-Kingdom-XXXXXX networks, then lets the parent select one. The app
connects using the shared dragon password, checks the lamp hostname matches that
SSID, and still requires a separate click to install. It tries to rejoin the same
AP after reboot and restore the original computer Wi-Fi after success, failure,
mode change or close. Manual connection remains available if OS policy blocks
Wi-Fi control. Home Wi-Fi keeps the existing shared-network discovery workflow.

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
local home network. No USB, firmware bundled into the app, Wi-Fi password input,
automatic install, factory reset or cloud backup. The same application fetches
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
1â€“3 and 0.3.0 stable use the explicit format-1 bridge to the same calibration-aware
image; later firmware uses format 2. Backup must be saved before START. Uncertain
chunk acknowledgements are checked by offset before retrying (beta 3 rejects
duplicates). Cancellation aborts before finalization. After finalization the app
waits for validated startup and compares persistent backup fields, excluding
volatile phone time/timezone rules and CRC. No automatic backup restore.

Backups contain personal settings and stay in the OS user's private application
data folder. Keep private. Physical lighting/touch/power checks remain necessary.
