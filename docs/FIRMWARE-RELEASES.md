# Firmware releases and local preparation

**Shipping stable:** v0.3.0, promoted from beta 2. **Calibration-aware published beta:**
v0.3.0-beta.3. **Local development:** v0.3.0-beta.4, unpublished and awaiting physical
acceptance. The corrected C3 must retain calibration-aware firmware. The exact
firmware mix already dispatched has not been inventoried.

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
