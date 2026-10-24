# Shipping reliability implementation - 24 October 2026

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
| Batch acceptance permits missing identity/validation and bare-board zero budget | Both launchers use signed production recovery. Expected board/tag, hashes/layout, preserved NVS, VALID app, increasing uptime and 400 mA USB estimate required. Developer checks explicitly cannot grant product acceptance. | Serial/GUI/ROM/USB operations simulated; wrong/missing identity and zero budget block checks. Physical batch verification pending. |
| Clean Python tests rely on undeclared crypto; packaging in ignored scripts | Pinned test/service dependencies, explicit CI install, generated-header check, maintained immutable preparation with external key, source commit/fingerprint and toolchain. | Clean virtual-environment Python tests and ephemeral-key package preparation tests. No real release key used or release signed. |
| Lost offline chunk reply forces restart | Three bounded browser retries; server acknowledges only the exact last duplicate without rehash/write. Changed duplicate or wrong offset rejected. Cancel aborts; retry starts anew. | Actual-handler duplicate/content/offset tests; physical complete/interrupt/retry uploads pending. 512-byte bound retained. |
| Large page copy/poll overhead | Deterministic gzip page when supported, raw fallback; hidden-page polling paused, refresh on return, failure backoff capped at 30 s. | Embedded page 50,621 UTF-8 bytes versus 15,702 gzip bytes (69% smaller payload). Round-trip test and phone simulation pass. Heap/TLS/page latency on C3 still to measure. |
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

57 Python tests pass in a fresh isolated virtual environment using the declared
pinned dependencies. All 17 native suites pass using Zig 0.13.0. The existing
390x844 Playwright/Edge simulated phone workflow and generated-header consistency
check pass. Real RSA tests use ephemeral test keys and do not alter the trust root.
The initial fresh Arduino build exposed an auto-prototype namespace issue, fixed
by qualifying signature types; both pinned target builds subsequently completed.
Final source-build sizes/hashes are recorded below after the committed rebuild.
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
