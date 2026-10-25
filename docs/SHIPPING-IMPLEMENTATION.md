# Shipping reliability implementation - 24 October 2026

## Publication checkpoint - 25 October 2026

At the owner's request, firmware 0.3.1 and Windows/Mac updater 1.0.0 are published.
The revised manual was published first. The signed beta-3 Wi-Fi bridge passed a
real S3 installation with preserved settings and validated startup. See
[the current release record](RELEASE-0.3.1-2026-10-25.md) and the
[family guide](https://sai021.github.io/dragon-kingdom/update/).
Earlier unpublished/checklist statements below are historical checkpoints.


The initial beta-4 implementation below is superseded by the [beta-6 parent-page and GitHub transport follow-up](PARENT-PAGE-FIXES-2026-10-25.md), including live corrected-C3 Wi-Fi acceptance and current build hashes. Earlier no-device statements describe the initial software-only checkpoint.

## Baseline and scope

Branch `codex/shipping-reliability` starts from beta 3 development `7b0d9dc`.
The local shipping release ref remains `codex/release-0.3.0` at `6c52456`, promoted
from beta 2. Release identity here is based on repository records/local refs,
not a new hosted-release audit. The exact shipped mix remains unknown.
Existing README/status edits and the supplied shipping review were preserved.
Local candidate identity is `v0.3.0-beta.4`; it has not been published or flashed.
No hardware, supplied CAD/STL/BOM/Gerbers, pins, trust root, power ceiling, network
locking, All protection, catalog IDs or saved-data layouts were changed.

## Implemented changes and evidence

| Original failure | Candidate behavior | Software evidence and remaining physical gate |
| --- | --- | --- |
| Any different online tag offered; offline metadata lacks version/capability | Signed format 2 binds tag, board, size/hash, capability and schema. Newer-only upgrades; explicit compatible Return to Release. Calibrated units cannot lose correction. | Handler tests reject absent/old/equal/incompatible metadata before erase; real RSA tests bind compatibility/tag and reject tampering. Both-board physical OTA/bridge/rollback pending. |
| Ordinary degraded boot attempts rollback every loop | VALID, trial, migration and unknown states are distinct. Only trial rejection rolls back, once; missing target/API failure retains diagnostics. Rotation joins required startup stores; internet is not required. | Native tests exercise the same decision policy. Fresh Arduino builds compile the adapter. Actual bootloader state/fallback tests remain required. |
| Home Wi-Fi never rejoins after success | Station-only retries with 10-second to 5-minute backoff and bounded attempts; saved credentials are not rewritten on rejoin. mDNS restarts on reconnect/address change. No later setup-AP reopen. | Backoff/rollover/busy policy tests; actual ESP driver, DHCP and router-outage tests pending. Touch loop has no added retry delay. |
| Corrupt restore journal blocks startup indefinitely with no service escape | Valid transactions remain retryable and retained. Invalid journals can be explicitly abandoned over USB only after private evidence capture. No automatic discard. | Actual-handler corruption, interrupted record-write, partial journal-write, storage-failure and retry tests preserve calibration. Exhausted real NVS and interruption timing remain physical gates. |
| Batch acceptance permits missing identity/validation and bare-board zero budget | Both launchers use signed production recovery. Expected board/tag/running-image digest, hashes/layout, preserved NVS, VALID app, increasing uptime and 400 mA USB estimate required. Developer checks explicitly cannot grant product acceptance. | Serial/GUI/ROM/USB operations simulated; wrong/missing identity and zero budget block checks. Physical batch verification pending. |
| Clean Python tests rely on undeclared crypto; packaging in ignored scripts | Pinned test/service dependencies, explicit CI install, generated-header check, maintained immutable preparation with external key, source commit/fingerprint and toolchain. | Clean virtual-environment Python tests and ephemeral-key package preparation tests. No real release key used or release signed. |
| Lost offline chunk reply forces restart | Three bounded browser retries; server acknowledges only the exact last duplicate without rehash/write. Changed duplicate or wrong offset rejected. Cancel aborts; retry starts anew. | Actual-handler duplicate/content/offset tests; physical complete/interrupt/retry uploads pending. 512-byte bound retained. |
| Large page copy/poll overhead | Deterministic gzip page when supported, raw fallback; hidden-page polling paused, refresh on return, failure backoff capped at 30 s. | Embedded page 50,785 UTF-8 bytes versus 15,711 gzip bytes (69% smaller payload). Round-trip test and phone simulation pass. Heap/TLS/page latency on C3 still to measure. |
| Support needs private serial captures | Parent-only JSON export contains firmware/board, reset reason, uptime, OTA/startup state, estimated ceiling, calibration flag and connection/heap metrics. | Whitelisted response inspected; no password/token/SSID/child-name fields. Physical support capture remains pending. |
| Repeated unchanged rotation saves write NVS | Read/compare existing valid record and skip unchanged writes. | Native assertion verifies no extra write; existing persistence/conflict behavior retained. |
| Printed/current guides describe removed login/purple hold | Coordinated parent/manual/setup/rear-label update; historical guides explicitly archived. QR destination unchanged. | All eight manual pages plus card and labels rendered and visually inspected locally. Actual print/phone scan acceptance pending. |

Saved schema 1 is unchanged. USB recovery conservatively requires calibration
support even when its presence is unknown; future/custom source schemas need a
separate reviewed migration. Older installed firmware needs the explicit offline
v1 bridge or signed USB recovery described in [the transition guide](UPDATE-COMPATIBILITY.md).
It cannot gain the new enforcement merely from publishing new metadata.

## Usability and measured scope

Home-address guidance now survives browser restarts in localStorage. Existing
stale-generation conflict rejection and in-memory editor draft retention remain;
no silent overwrite was introduced. Persisted editor drafts were considered but
not enabled: the shared setup-IP origin needs device-bound draft ownership and a
restore/discard flow before storing child-created names there. Existing wording
separates temporary play glow from saved starting glow and explains offline clock
resynchronization. No framework, WebSockets or cloud service was added.

Larger upload chunks and render/transmission optimizations remain measurement-led
follow-ups; increasing bounds without real C3 heap/touch measurements would not
establish an improvement. The fixed 512-byte framing, signature checks and current
limits are retained. A host rendering profile is local diagnostic evidence only,
not a claim about ESP32 loop latency or a rendering speedup.

## Verification and release gates

59 Python tests pass in a fresh isolated virtual environment using the declared
pinned dependencies. All 17 native suites pass using Zig 0.13.0. The existing
390x844 Playwright/Edge simulated phone workflow and generated-header consistency
check pass. Real RSA tests use ephemeral test keys and do not alter the trust root.
The initial fresh Arduino build exposed an auto-prototype namespace issue, fixed
by qualifying signature types; both pinned target builds subsequently completed.
Final fresh builds completed from committed source `6b69972` (ESP32 core 3.2.1,
Adafruit NeoPixel 1.12.5). Actual downloadable application sizes and whole-file
SHA-256 values:

| Board | Application bytes | SHA-256 |
| --- | ---: | --- |
| S3 | 1,393,344 | `9a821eb4165e0f11bcd02bc2abfe695c450c56007765598c3c992008256e33e6` |
| C3 | 1,437,584 | `f90288f48628b0d5f22fd772fb019b79a7c6d6b3b8db7e9839341538b694d450` |

Both fit the 1,572,864-byte application slot. Compiler static RAM: S3 62,932 bytes;
C3 53,888 bytes. Per-board ignored `build/<board>/provenance.json` records the full
commit, source fingerprint, toolchain and application/bootloader/partition hashes.
These are unsigned build outputs; signing and publication have not happened.

No cached compile/link output is presented as a fresh build.

No connected device was probed, flashed or power-cycled. No physical acceptance,
shipping-ledger pass, actual mobile captive portal, router lifecycle, full OTA,
bootloader rollback, external-power or overnight result is claimed.

Before publication:

1. Inventory the firmware mix already shipped and identify calibration-aware units.
2. Run [both-board physical acceptance](PHYSICAL-ACCEPTANCE.md), preserving private
   evidence and entering real functional results in the ignored local ledger.
3. Supply the existing external signing-key path; prepare immutable assets from
   the exact accepted source/build provenance. Review the v1 bridge transition
   alongside v2 assets and preserve recovery downloads for older firmware.
4. Review the local corrected PDF artifacts, print/phone scan them and confirm
   the existing `https://sai021.github.io/dragon-kingdom/manual.pdf` destination.
5. Obtain explicit authorization to publish releases/channel pointers, replace
   hosted assets or flash any physical device. These are separate actions.


USB source-schema gate: runtime now reports its saved-data schema. Recovery refuses
unknown or mismatched source schemas before any write. Known stable 0.3.0/beta 1-3
use the historical schema-1 contract. For an unbootable or unreported legacy image,
first retain a verified private raw NVS dump with `restore_service.py`, review its
original firmware/schema, then deliberately supply `--source-schema 1` to CLI recovery.
This service assertion is never inferred by Auto mode and does not bypass signed
target compatibility. A future schema needs a separate migration, not this assertion.

Production startup compares the cached running ESP image SHA-256 to the signed
bundle application's validated appended digest. An equal tag alone cannot pass a
changed image. This ESP image digest differs from the whole-file download SHA-256;
both are checked for their respective purpose. Build provenance also binds image
hashes and refuses source changes during compilation.

Final browser regression also verifies identical retry payloads after a lost acknowledgement,
explicit Return to Release intent, hidden-tab suppression and return refresh, support
JSON download, and cancellation while the last chunk is in flight. The final-chunk
cancellation test exposed and fixed an unintended finalize-after-cancel path. Production
serial simulations reject wrong board, wrong/missing image digest and OTA state 20
(which must not be mistaken for VALID state 2). All 59 Python tests pass after this fix.
