# Dragon Kingdom Updater

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
