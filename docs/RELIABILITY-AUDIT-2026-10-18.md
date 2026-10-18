# Reliability audit — 18 October 2026

Follow-up: [19 October repairs and verification](RELIABILITY-FIXES-2026-10-19.md).
The findings below preserve the pre-repair audit evidence.

The current workspace is a capable development prototype, but it is not ready
for a family release. Two reproduced defects can change the meaning or contents
of saved collections. Browser recovery, low-power budgeting and release tooling
also need correction. Passing builds and the existing tests do not cover these
failure paths.

This audit covers the working tree, including the existing uncommitted and
untracked work. Production sources, palettes, generated product headers, saved
flashing selections and connected devices were not changed. New audit harnesses,
synthetic data, build outputs and logs are under ignored
`dragon-firmware/.tools/reliability-20261018/`. No device was flashed or reset,
and no new physical evidence is claimed.

## Verification results

| Check | Result | What it establishes |
| --- | --- | --- |
| Existing Python regressions | **23 passed, 1 failed** | Current catalog differs from the dated colour fixture; see R7 |
| Existing native C++ suites | **13/13 passed**, run separately after the Python failure | Core, rendering, sensors, startup, storage, C3 simulation, alarm and connection policies |
| Existing browser suite | **Passed**, Playwright 1.62.1 / headless Edge, 390×844 | Existing mocked phone workflows |
| Additional browser fault injection | Reproduced R3, R4 and R8 | Initial alarm failure, misleading busy selector and empty-profile reload |
| Actual library HTTP route with fake transport/storage | Reproduced R1 | An outdated form overwrites a different profile and receives HTTP 200 |
| Catalog upgrade with a real binary library record | Reproduced R2 | Adding a preset silently changes an existing favourite from custom to supplied |
| Power model accounting | Reproduced R6 | 300 mA fallback has a 314 mA minimum including the stated Wi-Fi reserve |
| Partial batch build | Reproduced R5 using simulated compiler outputs | Failed C3 build leaves new S3 and old C3 selected |
| Accelerated renderer stress | **180,000 frames passed** | All ten modes, maximum-white customs, sunrise, random timer values and 400–2400 mA limits including Wi-Fi allowance |
| Accelerated schedule | **365 starts and 365 completions passed** | One UTC daily alarm per day through multiple 32-bit `millis()` rollovers |
| Corruption sweep | **6,560/6,560 single-bit corruptions rejected** | Checksum/validation of every bit in an 820-byte populated library record |
| Generation rollover | **Passed** | Save/reload across `0xffffffff` to zero, followed by failed-write retention |
| Product Arduino builds | **S3 and C3 passed** | Current editable sources compiled in an isolated copy |
| Standalone tester builds | **BoardTester and MatrixTester passed** | S3/default partitions; compilation only |
| Generated headers | **Matched editable source** | Neither palette nor page header was stale |
| Existing saved S3/C3 bundles | **Checksums valid** | Integrity of existing selections; the audit did not replace them |
| Browser dependency | Pinned Playwright 1.62.1 resolved successfully | Package exists; audit used that same version |
| Diff whitespace check | Passed; Git emitted line-ending notices | No whitespace errors found in the existing diff |
| 21 September Gerber reconstruction | **No shorts or opens across 30 plated holes** | Rerun on an isolated copy of the older prototype, not native CAD DRC |
| Stored optical chamber grid | **All ten zones reach their own front region; no detected cross-zone connection** | Rerun of connectivity logic on the existing grid, not a fresh mesh build or physical optical test |

Product build details:

| Target | Compiler application usage | Upload image bytes | Static RAM |
| --- | ---: | ---: | ---: |
| S3 | 1,147,710 | 1,147,856 | 51,300 |
| C3 | 1,171,742 | 1,171,888 | 42,256 |

Both upload images fit the actual 1,572,864-byte product application partition.
Compiler output still displays a generic 16 MB maximum; that is not the product
partition capacity. The audit builds retain network-event locking, the 400 mA
computer-USB ceiling, protected All and existing storage layouts.

S3 application SHA-256:
`2513c79a46b06869dbe32bad1a26cc917b2478376e05fc4d29ae43c127ed5db3`.
C3 application SHA-256:
`12cdafc4b5714c8130f90a7fe1474f8e7fc63bb17eb5f47352c7656ce8de8ff3`.
These identify audit builds only, not installed firmware or replacement release
bundles.

BoardTester compiled at 339,670 bytes of application storage and 21,092 bytes
of static RAM. MatrixTester compiled at 324,438 bytes and 20,804 bytes. Both
used their documented default partition configuration and were not uploaded.

## Findings, in repair order

### R1 — P1: A stale form can overwrite another child's profile

**Source:** `dragon-firmware/DragonPrototype/LibraryWeb.h:31–40` and
`dragon-firmware/web/library.js:21`.

Profile updates derive their destination from `library.data.active`. The browser
sends the name, glow and favourites, but no intended profile ID or library
generation. If browser A is editing Child A while browser B selects Child B,
the next save from A writes A's form into B. Three-second polling cannot prevent
the race, and polling is skipped while A has a command pending.

**Reproduction:** execute the actual registered `/api/profile` handler with two
existing profiles. Select profile 2, then submit the previously loaded profile 1
update. The response is 200. Profile 1 remains `Child A`; profile 2 becomes
`Child A edited`, with A's submitted brightness and favourite. This used the
real route and library implementation with a fake HTTP transport and NVS.

**Repair:** bind every collection mutation to an explicit profile identity and
expected library generation. Reject stale requests with 409 before changing
anything. Include custom creation/copy operations, which also take their owner
from the global active profile. Preserve drafts when reporting a conflict.
Add a two-client interleaving regression using the real handlers.

### R2 — P1: The supported preset clone command breaks saved custom IDs

**Source:** `dragon-firmware/tools/palettes.py:179–185` and
`dragon-firmware/DragonPrototype/DragonLibrary.h:15,36–40,73–76`.

Custom IDs are `PRESET_COUNT + slot`. The documented `clone ID NEW_ID` command
appends a supplied preset, increasing `PRESET_COUNT`, but the stored version-1
record contains no catalog size or migration information. A perfectly valid old
record therefore loads under a changed ID interpretation.

**Reproduction:** create an 81-preset binary record whose favourite 81 is named
`Original custom`. Generate a header with one appended preset and load the same
820-byte record. Validation still passes. Favourite 81 resolves to the new
supplied preset; the original custom now has ID 82. Other custom favourites can
point to the wrong custom slot or make an older snapshot invalid.

**Repair:** immediately prevent catalog count/order changes in the supported
editor/build path until a migration exists. Longer term, reserve a stable custom
ID range and version/migrate stored IDs using the old catalog identity. Do not
erase user libraries as a workaround. Colour edits that retain IDs and count do
not trigger this defect.

### R3 — P2: An initial alarm-load failure leaves an unsafe recovery path

**Source:** `dragon-firmware/web/dragon-kingdom.html:78–87,111–114,127–130`.

If the initial GET `/api/alarm` fails once, `alarmState` stays null. Later refreshes
only fetch the alarm when `alarmState` already exists, while initialization is
only retried when the library is absent. Play can recover while alarm loading
remains permanently failed until a page reload or another alarm action.

**Reproduction:** return 503 for the first alarm GET and succeed for subsequent
requests. Four successful explicit refresh cycles issue no second alarm GET.
Then click **Set clock from my phone**. The returned alarm is enabled at 06:00
for 45 minutes, but the form still displays disabled / 07:00 / 20 minutes and
Save becomes enabled. Saving now can replace the actual schedule with defaults.

**Repair:** track alarm initialization separately, retry transient load failures,
and populate the form from a successful authoritative read before enabling Save.
Retain the existing protection for genuine unsaved alarm edits.

### R4 — P2: A busy profile selector displays a change that never happened

**Source:** `dragon-firmware/web/library.js:17–19` and
`dragon-firmware/web/dragon-kingdom.html:93–99`.

The profile change handler returns immediately when `commandBusy` is true, after
the select element has already changed. It neither disables the selector nor
restores its old value. Normal state polling does not correct that selector when
the device's profile has not changed.

**Reproduction:** with All loaded and another command pending, select Child.
The select displays Child, `collection.active` remains zero, and no profile POST
is sent. This extends the previously documented dropped-click behaviour into a
misleading persistent profile display.

**Repair:** disable applicable controls during a command, or explicitly restore
their authoritative values when refusing an action. If actions are queued,
retain their intended profile identity and handle failures before draining them.

### R5 — P2: A failed batch build publishes a mixture of firmware revisions

**Source:** `dragon-firmware/tools/batch_flash.py:142–155,261–280`.

`compile_targets()` publishes each target's manifest immediately. If S3 succeeds
and C3 fails, S3 has already been replaced while C3 remains the old image.
The error handler restores the Flash button because `bool(self.builds)` is true.
Both images have valid hashes, so integrity checking does not catch the mismatch.

**Reproduction:** seed valid old S3/C3 bundles, simulate successful S3 compilation,
then fail C3. Result: `{"s3":"new","c3":"old"}`. Existing tests only fail the
first target and therefore miss partial publication.

**Repair:** stage and validate both targets before publishing a release-set
manifest, or mark target freshness explicitly and block the failed target from
appearing ready for the requested build. Include a source fingerprint and test
failure on the second target as well as the first.

### R6 — P2: The 300 mA fallback cannot accommodate the stated Wi-Fi reserve

**Source:** `dragon-firmware/DragonPrototype/DragonPrototype.ino:253–255,556`,
`PowerPolicy.h:18–30`, and `Config.h:35–37`.

The lowest passing startup ceiling is 300 mA, and any nonzero ceiling starts
networking. Rendering subtracts 200 mA for the controller and another 50 mA for
Wi-Fi, leaving 50 mA for a panel whose model includes 64 mA of idle draw.
Black pixels cannot reduce that modeled idle draw.

**Reproduction:** compose a frame at `operatingTotal=300`. Panel estimate is
64 mA; adding the stated controller and Wi-Fi allowances totals **314 mA**.
Existing current assertions omit the extra 50 mA and therefore pass. The
extended 400–2400 mA stress checks include it and pass.

**Repair:** give networking a minimum feasible budget, or retain a touch-only
fallback when the available budget cannot cover controller, radio allowance and
panel idle. Use one shared total-current calculation in runtime diagnostics and
tests. This is an inconsistency in the software estimate, not a measured 14 mA
electrical overrun, and does not justify raising the USB ceiling.

### R7 — P2: The normal regression command currently stops before native tests

**Source:** `dragon-firmware/tests/test_matrix_import.py:40` and
`dragon-firmware/tools/run_tests.py:18`.

The test requires editable catalog colours to equal a dated audit fixture.
Current differences include Sundew wings, Clay edges, Blaze edges, Flame face,
and Clearsight face/body. The first failure is Sundew `#00AA00` versus the
fixture's `#245C30`. Both generated headers match their current editable sources.

**Impact:** the documented runner exits after Python tests; native tests and
later browser steps in that CI job do not run. This is not evidence that the
current colour edits are wrong. Reverting them to satisfy an old fixture would
discard existing work.

**Repair:** separate structural/storage compatibility assertions from historical
colour evidence. Record intentional colour revisions in the audit trail, and
run independent test groups so one failure does not hide the other results.

### R8 — P3: Reloading an empty profile enables controls that cannot work

**Source:** `dragon-firmware/web/dragon-kingdom.html:128` and
`dragon-firmware/web/library.js:12–13`.

`populateDragons()` correctly disables play controls for an empty named profile,
but `initialize()` then unconditionally enables the dragon and brightness
selectors. This only appears on initial load/reload, so the existing test that
creates an empty profile after initialization passes.

**Reproduction:** start the page with an empty named profile active. Sleep is
disabled, but dragon and glow are enabled while the only dragon option says
“Add favourites or make a dragon”. The firmware rejects play requests with 409.

**Repair:** let collection availability determine control state after
initialization, including after reconnects and page reloads.

### R9 — P2: CI does not compile the supported C3 product target

**Source:** `.github/workflows/checks.yml:42–43`.

CI invokes `dev.py build` without a board argument, which defaults to S3.
The native C3 suite substitutes hardware and excludes the actual Wi-Fi adapter;
it cannot catch target-specific ESP32 core/linker failures. C3 builds in this
audit passed, but future C3 regressions would not be gated by CI.

**Repair:** add an S3/C3 build matrix and partition checks for both. Keep browser,
Python and native results visible independently. A lockfile would also make the
Node installation more reproducible; the pinned Playwright version itself was
available and matched the audit runtime.

## Network service risk found by source inspection

`DragonWeb.h:148` calls synchronous `WebServer::handleClient()` from the same
loop that advances touch, rendering, USB checks and the sunrise. The installed,
pinned Arduino-ESP32 3.2.1 source sets a 5,000 ms client timeout before parsing;
request/header reads block, and the body reader renews its wait for each chunk.
Authentication runs after parsing. There is no project-level whole-request
deadline or body-size limit before that work.

A partial or trickling request can therefore delay local controls and animation
updates. This conclusion comes from the actual local dependency source, not a
live denial-of-service test. No crash or specific physical stall was induced.
Treat bounded HTTP processing as a release requirement. Test an incomplete
request, oversized body, slow reader and disconnected client while measuring
maximum loop delay, missed touch gestures, free heap and alarm progress. Any
network-task separation must preserve the existing network-event locking and
serialize shared lighting/library state.

Also test **Forget Wi-Fi during an outstanding join**. That route clears the
software state and calls `WiFi.disconnect()`, whereas the same source already
documents why a disconnected-but-associating station needs to be stopped.
The pinned core returns early from `STAClass::disconnect()` when not connected.
No new live evidence establishes that cancellation is complete in this case.

## Hardware, mechanical and documentation boundaries

The September Gerbers and existing optical files remain earlier prototypes.
The previously identified R4 5 V pad entry has only about 0.05079 mm ideal
overlap; its documented routing correction, native DRC and physical fit remain
open. Software current models cannot establish supply capacity, transient
behaviour, temperature or short-circuit protection. The newer printed STLs,
build photographs and final Gerbers have not been supplied for this audit.

The current firmware map is **BG 0, LW 13, RW 16**, plus four pixels per wing
edge. The older optical metadata is **BG 10, LW 9, RW 10**, with the same edge
counts. `docs/MECHANICAL-ASSETS.md` still describes the intermediate firmware
map BG 6 / LW 11 / RW 12. Resolve the map against the final assembled optics;
do not change an older design merely to make these numbers agree.

Other documentation drift worth correcting:

- `docs/ARCHITECTURE.md` says 20-second Wi-Fi timeout; the implementation is
  60 seconds. It describes a unique setup key and omits the alarm NVS/API entries.
- `docs/PROVENANCE.md` says device credentials are generated and public docs do
  not contain the prototype password, while current firmware/docs deliberately
  use a shared published access key. Existing third-party asset notices remain
  applicable; no licence change is part of this audit.
- `dragon-firmware/DRAGON-PALETTES.md` advertises up to 255 presets,
  but firmware reserves eight byte-addressed custom slots and currently
  supports at most 248 presets even before considering R2.
- `tools/verify_presets_live.py` still hard-codes COM17 and disables DTR. It
  should accept and validate the current port and use the established native
  USB CDC settings before being reused. It was not run.

Physical release evidence still needed: iPhone/Android setup and recovery;
concurrent phone/touch use; router loss/recovery and long uptime; complete power
loss with NTP recovery; C3 boot strapping, ADC calibration and actual USB ceiling;
deployed-supply current, transient and thermal behaviour; final enclosure,
socket and optical fit. Laptop USB and external/main power must remain mutually
exclusive in the current circuit. Saved timezone rules also have a finite
400-day horizon and need a maintained refresh/recovery path.

## Repair and retest sequence

1. Address R1/R2 before shipping any firmware that changes collections or the
   catalog. Retain old-record fixtures and prove migration without data loss.
2. Fix alarm initialization and busy-control handling, then run two-client,
   timeout-after-save and reconnect tests against actual HTTP routes.
3. Correct the minimum networking budget and bound HTTP work; add tests that
   include every stated current reserve and measure loop responsiveness.
4. Make multi-target publication consistent, restore the regression gate and
   add C3 CI. Produce one source-fingerprinted release set only after all checks
   pass.
5. Perform the physical release matrix separately, recording board revision,
   firmware hash, supply, network conditions and results. An accelerated host
   test is not an endurance test of the radio, flash hardware or power supply.

Local evidence: `native-results.json`, `build-results.json`, per-suite/build
logs, `api_failures.cpp` / `api-failure-results.txt`, `catalog_migration.py` /
`catalog-migration-results.txt`, `browser_failures.cjs` /
`browser-failure-results.json`, `partial_build.py` /
`partial-build-results.json`, `stress.cpp` / `stress-results.txt`, diagnostic
build logs, `gerber-2026-09-21.log`, `historical-chambers.log`, and
`source-manifest.json`, all under the ignored audit directory. Mechanical
dependencies were installed locally there after the bundled Python lacked
SciPy/Matplotlib; original CAD and chamber outputs were preserved. These
records contain synthetic/test data, not household
credentials. The report records findings; it does not claim they have been fixed.
