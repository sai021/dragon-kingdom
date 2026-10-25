# Firmware releases and local preparation

**Shipping stable:** [v0.3.1](https://github.com/sai021/dragon-kingdom/releases/tag/v0.3.1), preserving beta-9 application behavior and C3 calibration, with lower night glow, low-light colour rounding, parent dropdowns and the long-redirect HTTPS repair. See [release evidence](RELEASE-0.3.1-2026-10-25.md).

The owner confirms shipped lamps run beta 3. Their old HTTPS downloader cannot be relied on; use the [Windows/Mac desktop updater or phone-only repair instructions](https://sai021.github.io/dragon-kingdom/update/) for a deliberate format-1 signed bridge once. Ordinary format-2 files are for beta 4+ and future updates. Both formats contain the same board-matched calibration-aware application. Older 0.2.x devices require signed USB migration. Do not install beta-2-based old stable 0.3.0 on corrected C3 units.

GitHub latest points to firmware 0.3.1; normal new-format Release discovery follows it. Publish desktop updater releases with `--latest=false` so they cannot replace the firmware pointer. Historical firmware-beta assets remain unchanged; the desktop app offers main releases only.

Release is the default update channel; Beta is an explicit parent choice. Both
require a parent to check and install. Home Wi-Fi with internet and a synchronized
clock is needed for online checks. Setup Wi-Fi has no internet. For offline updates,
download a matching signed file first, then reconnect to the dragon and upload it.

Beta 4 uses [signed format 2 and an explicit bridge transition](UPDATE-COMPATIBILITY.md).
Normal updates require newer compatible versions. Intentional Return to Release
is separate, still checks capabilities/schema, and must never remove a calibrated
unit's voltage correction. Missing old-format metadata is rejected before erasing
an update slot. Existing firmware needs a deliberate v1 bridge or signed USB recovery.

Use maintained `tools/prepare_release.py` with external signing-key paths and fresh
both-target build provenance. It never publishes, flashes or creates a trust root.
Do not use ignored historical packaging scripts. `Flash Dragons.cmd` and
`Recover Dragon.cmd` both open the signed recovery workflow. The older developer
flasher cannot accept unsigned caches for writes and cannot grant production acceptance.

After the [physical checklist](PHYSICAL-ACCEPTANCE.md), review immutable image hashes,
source commit, dependency versions, compatibility fields, signing verification,
printed artifacts and release notes. Then request separate authorization to publish
release assets, change channel pointers, or replace the hosted manual. Preserve
`https://sai021.github.io/dragon-kingdom/manual.pdf` for already-printed QR codes.
Keep historical bundles and the explicit bridge available for existing customers.
