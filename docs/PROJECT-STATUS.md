# Project checkpoint — 25 October 2026

## Current updater: Easy Update 1.5.0, including USB Auto

The owner requested USB updates inside Easy Update and clarified that Auto mode
must remain the primary workflow. USB cable mode confirms USB-only power once
for the whole batch, prepares signed USB files, then handles one native Espressif
USB board at a time. Older supported firmware updates; equal versions are checked
without rewriting and newer versions are skipped. The existing BatchGate requires
unplugging before the next board and prevents re-enumeration triggering a second
update. Stop finishes the current write/checks; errors stop Auto. Manual selection
remains available for other bridges. AP batch and Home Wi-Fi modes are retained.
See [implementation and publication evidence](UPDATER-1.5.0-2026-10-25.md).
Firmware remains 0.3.1. USB firmware writes have not been physically tested for
this desktop integration; signed download/cache and simulated service checks are
separate from actual port enumeration and packaged launch tests.

## USB recovery port discovery repaired

Flash Dragons.cmd launches recovery_gui.py. Its port scan previously ran only
following signed-bundle validation, so opening without a selected bundle showed
no ports. Discovery now runs independently before bundle checks and every second
while idle; single/newly connected ports are selected automatically. Changing
selection clears the USB-only confirmation. Batch opt-in, per-batch power checks
and signed firmware gates remain intact. Regression checks cover missing/invalid
bundles, hotplug/removal, retry after scan error and no implicit firmware writes.
A read-only test with the actual launcher Python/runtime found COM17 in the hidden
recovery window with no selected bundle. No serial port was opened and no firmware
was written; simulated hotplug evidence is separate from actual enumeration.

## Earlier updater: Easy Update 1.4.0

Startup checks the signed latest stable firmware and prepares the complete offline
set automatically, preserving the prior verified cache on failure. Startup never
installs firmware or changes Wi-Fi. Find & update all dragons explicitly scans
Dragon setup networks, joins each in turn and updates only older versions. Current
or newer lamps are skipped; results list each outcome and backup. Stop aborts
before finalization, or finishes the current restart check and skips the rest.
Wi-Fi restoration failure stops the batch. Home Wi-Fi mode remains necessary
for already home-connected lamps. Firmware remains 0.3.1.
See [implementation and publication evidence](UPDATER-1.4.0-2026-10-25.md).

## Earlier updater: Easy Update 1.3.0

The app is now named Dragon Kingdom Easy Update and opens in direct/offline mode.
The parent password is prefilled, editable and memory-only; one Update selected
dragon click starts backup and verified installation without a second confirmation.
Home Wi-Fi mode remains required for already home-connected lamps, whose setup AP
closes 15 seconds after joining home Wi-Fi. Connecting alone does not install.
The family guide, manual edition 1.3 and class sheet recommend Easy Update first.
Firmware remains 0.3.1. See [publication evidence](UPDATER-1.3.0-2026-10-25.md).
Earlier updater checkpoints below are historical.

## Earlier updater: 1.2.0 automatic AP discovery/connection

At the owner's request, direct mode now scans encrypted Dragon-Kingdom networks,
connects to the selected AP, checks the lamp identity, attempts reboot reconnection
and returns to the original computer Wi-Fi. Installation still needs a separate
click. Manual connection remains available if OS Wi-Fi/location access is denied.
Thirty-one tests and all three platform package jobs pass. A real Windows native
scan/join/read/return test succeeded against a beta-3 S3 without writing firmware;
physical Mac association and reboot-radio handover remain untested.

Corrected restriction: beta 3 and current firmware close AP 15 seconds after joining
saved home Wi-Fi, regardless of attached clients. Use Home Wi-Fi mode for those
lamps. Direct writes now refuse a home-connected lamp before login or flash START.
The guide, manual edition 1.2 and class sheet state this restriction and explain
automatic connection. Firmware remains 0.3.1 and GitHub latest still points to it.
See [current implementation and publication evidence](UPDATER-1.2.0-2026-10-25.md).
Earlier updater checkpoints below are historical.


## Updater 1.1.0: home and direct setup Wi-Fi

Published at the owner's request with two explicit modes. Home Wi-Fi keeps the
shared-network workflow; direct mode downloads the signed release first, then
asks the parent to join the dragon's setup Wi-Fi and connects to 192.168.4.1 with
no home setup or internet during transfer. Offline files survive app restart and
are fully reverified; partial downloads retain the previous complete set. Parents
switch Wi-Fi themselves. Twenty-one tests and packaged Windows/Apple Silicon/Intel
Mac checks pass, including real signed downloads and offline reload. Physical AP
association/reboot handover remains untested; firmware itself remains 0.3.1.
The manual and class notice now explain both modes at unchanged QR addresses.
See [implementation and publication evidence](UPDATER-1.1.0-2026-10-25.md).


## Current publication: firmware 0.3.1 and family updater

The owner requested publication and now reports the S3 is working without restarts. [Main firmware 0.3.1](https://github.com/sai021/dragon-kingdom/releases/tag/v0.3.1) is published, with all five CI jobs passing at 2cb953a and all 11 uploaded assets matching the prepared signed files. It retains beta-9 behavior with only the version label changed. Shipped beta-3 lamps need the explicit format-1 bridge once. Both board packages preserve calibration and schema 1.

The revised ten-page manual was published FIRST at the existing printed-QR URL. Stable /update/ and /setup/ help and the one-page class notice are published. The desktop application supports Windows x64, Apple Silicon Mac and Intel Mac, with deliberate installs, signed verification, private backups and post-boot settings checks. Simulator tests and packaged launch checks are separate from physical acceptance. The app is not Windows certificate-signed or Apple notarized; the guide includes the phone-only alternative.

See [release record](RELEASE-0.3.1-2026-10-25.md), [family guide](https://sai021.github.io/dragon-kingdom/update/) and [desktop source](../desktop-updater/README.md). Older entries below describe earlier checkpoints and do not override this publication. No customer messages were sent and no broad field endurance result is claimed.


## Shipped inventory and beta-3 HTTPS issue — 25 October 2026

The owner confirms all units have shipped and all shipped units run v0.3.0-beta.3; the earlier unknown-firmware-mix statements are superseded. Board counts were not supplied. Beta 3 has the bounded-request HTTPS redirect issue fixed in beta 6+, so self-downloading a repair cannot be assumed. Its local Wi-Fi signed-file uploader remains a path that does not require opening the enclosure. It requires a format-1 legacy bridge, not the ordinary format-2 beta-9 package. Existing beta-9 bridges are cryptographically compatible, but beta 9 remains a prerelease with the unresolved S3 issue and old online discovery feeds. No bulk rollout, customer contact or channel change was performed. See [remediation options and draft parent workflow](SHIPPED-BETA-3-HTTPS-2026-10-25.md).

## S3 previous-firmware comparison — 25 October 2026

At the user's request, tested beta 9 → signed beta 8 → published beta 9 on the same laptop-USB-only S3, retaining the 400 mA ceiling. No captured reset in either five-minute beta-8 or return beta-9 observation; both had a failed support sample but continuously increasing retrieved uptime. Full-gain controlled phases were included. Both USB services preserved raw NVS exactly; final persistent settings matched. This does not reproduce a beta-9-specific fault or resolve the earlier intermittent resets. Left beta 9 VALID, automatic light restored and LEDs temporarily off; C3 untouched. See [conditions, limits and results](S3-FIRMWARE-COMPARISON-2026-10-25.md).

## S3 restart recurrence — 25 October 2026

The S3 restart problem recurred after the brief no-restart report. Live tests captured repeated uptime drops/power-on resets with USB detected and the 400 mA ceiling, including after temporary lights-off commands. The USB port also disappeared during a ROM-loader-only test; the board later returned to the normal application without an issued restart command. This points outside the Dragon application but does not isolate the USB/power/reset fault. Startup/lifecycle/current-limit native suites pass; no firmware or saved settings were written. The beta-9 release notes now flag the unresolved S3 issue. See [live tests and next physical isolation step](S3-RESTART-RECURRENCE-2026-10-25.md).

## Published beta 9 — 25 October 2026

[Beta 9 is published](https://github.com/sai021/dragon-kingdom/releases/tag/v0.3.0-beta.9) as an opt-in manual-download prerelease with ordinary format-2 packages, explicit legacy bridges and signed USB recovery. All five CI jobs pass at d207609; both application binaries are identical to those tested on the lamps. The user praised the colour accuracy and reported no restarts, with the latest power arrangement not separately confirmed. Stable latest, existing update feeds and hosted manual remain unchanged. See [publication verification and remaining acceptance](BETA-9-PUBLICATION-2026-10-25.md). Older candidate/local-only statements below are historical.

## Current colour candidate: beta 9 — 25 October 2026

Source `fc1b770` removes a low-light red bias by combining ambient/Glow scaling, rounding to nearest and retaining a symmetric RGB floor. 59 Python tests, 18 native suites, browser checks and both pinned builds pass; signed packages are local only. The corrected C3 runs beta 9 with VALID startup and preserved settings/calibration. Two S3 Wi-Fi uploads were interrupted before finalisation, followed by a user-confirmed uncommanded restart loop. The user then connected the main S3 to laptop USB with external power off. USB service installed beta 9 with all 20,480 NVS bytes unchanged, verified image/startup VALID, and increasing uptime through 70 seconds at the 400 mA USB ceiling. Both lamps now have beta 9. The cause of the external-power restart loop remains unproven; a known-good 5 V supply/cable test requires unplugging laptop USB first. Actual dark-room colour comparison remains pending. See [implementation, builds and live evidence](LOW-LIGHT-COLOUR-2026-10-25.md).

## Current candidate: beta 8 — 25 October 2026

The user's four-corner bench comparison led to a much lower automatic night-glow curve (about 1% to the existing 80% channel cap, before artwork/current/selected Glow reductions). Both lamps run beta 8 from `f524ddf`, with VALID startup, preserved settings/calibration and automatic light active. The separate USB bench board was not flashed. 59 Python tests, 18 native suites, browser checks and fresh both-board builds pass. See [exact scaling, bench observations and live evidence](NIGHT-GLOW-2026-10-25.md). The new dark-room/overnight result awaits user observation. Nothing was published.

## Current candidate: beta 7 — 25 October 2026

Both lamps run beta 7 from `89489b6`, with collapsed parent subsections, Connection & power, a support-download explanation and the user's backplate service instructions. Both Wi-Fi installs reached VALID startup and preserved settings and calibration presence. The live panels report product supply with an estimated 2,400 mA limit. 59 Python tests (clean rerun after a Tkinter teardown abort), 18 native suites, browser checks and fresh both-board builds pass. The nine-page manual edition 0.9 was rendered and inspected locally. See [implementation and live evidence](PARENT-DROPDOWNS-2026-10-25.md). Nothing was published; older candidate checkpoints below remain historical.

## User-reported checks on both lamps — 25 October 2026

Both beta-6 lamps (S3 and corrected C3) passed user-observed normal lighting, basic touch, room-light dimming/brightening, and normal-supply power-cycle with webpage reconnection. Detailed gestures, actual phone setup, router-outage recovery, rollback, restore interruption, USB acceptance, measured electrical/thermal behavior and overnight checks remain pending. These observations do not establish complete release acceptance.

## S3 Wi-Fi acceptance — 25 October 2026

The normal-supply-only S3 was identified on beta 2, backed up and updated over Wi-Fi using its signed beta-6 bridge. It reports VALID startup and preserved settings. Both update channels reach GitHub with no reported HTTPS errors; the live parent page selects the S3 package. See [S3 evidence and remaining physical gates](S3-WIFI-ACCEPTANCE-2026-10-25.md). Both the corrected C3 and this S3 now run beta 6. Nothing was published.

## Current candidate: beta 6 — 25 October 2026

Parent-page fixes and the GitHub long-redirect fix are committed at `69ba10a`. The corrected C3 runs beta 6 after a signed Wi-Fi update, with VALID startup, calibration present and saved settings preserved. Release checking now reaches GitHub and reports that compatible new-format online metadata is not published yet. 59 Python tests, 18 native suites, browser checks and fresh S3/C3 builds pass. See [changes, live evidence and hashes](PARENT-PAGE-FIXES-2026-10-25.md). Nothing was published; remaining physical acceptance is pending. Earlier candidate notes below are historical.

## Corrected C3 Wi-Fi acceptance — 25 October 2026

The corrected C3 was updated from beta 3 to beta 4 over Wi-Fi with laptop USB disconnected, using a locally signed legacy bridge. It rejoined Wi-Fi and reports VALID startup and calibration present. Saved user settings compared unchanged; only transient phone clock/timezone rules reset. Signed two-board assets are prepared locally; nothing was published. Physical LED/touch/LDR and remaining acceptance gates are pending. See [physical evidence and limitations](HARDWARE-TEST-2026-10-25.md). The implementation checkpoint below predates this live test.

## Current local implementation

Unpublished beta 4 is on `codex/shipping-reliability`, based on calibration-aware
beta 3. Stable shipping v0.3.0 remains beta-2-based and must not replace the
corrected C3 firmware. See [implementation, evidence and exact publication gates](SHIPPING-IMPLEMENTATION.md).
59 clean-environment Python tests, 17 native suites, simulated phone checks and
fresh pinned S3/C3 builds pass. The corrected eight-page manual, setup card and
rear labels are prepared and visually checked locally; the printed QR destination
is unchanged. Nothing was published or flashed. Physical acceptance is still
required. The dated sections below are historical checkpoints.


## Shipping review — 24 October 2026

The owner confirms hardware is made, firmware is loaded and shipping has started.
Hardware is fixed for further improvement work. See the
[detailed shipping review](SHIPPING-REVIEW-2026-10-24.md) for findings across
firmware, interface, updates, production tooling and customer instructions.
Fresh checks passed: 51 Python tests, 16 native suites and the existing simulated
phone-browser workflow. Additional handler probes reproduced an older signed-tag
offer and rejection/retention of a corrupt restore journal. No device was probed
or flashed, no fresh board build was performed, and no physical acceptance is
inferred from shipping status. Firmware and published artifacts are unchanged.

The review distinguishes stable 0.3.0 from beta 3; the exact mix already shipped
is not recorded here. Older dated entries below are historical evidence, not a
single description of current customer behavior.

## Beta 2 promoted to main Release — 24 October 2026

Owner requested beta 2 as the main release. GitHub latest now resolves stable
v0.3.0, built from beta 2 commit bf97f43 with only CURRENT_TAG renamed to v0.3.0.
Release-source commit 6c52456 is on codex/release-0.3.0; its isolated worktree is
.tools/stable-source. This primary checkout remains the beta 3 development line.
Stable manifests are signed for v0.3.0 and accepted by existing Release-channel
code; published binaries/packages/recovery checksums and signatures were checked.
43 Python tests, 16 native suites, browser simulations and both pinned cached-
dependency builds pass for the stable source. No board was flashed for promotion.

Already-installed beta 2 boards can stay as they are. The separately corrected C3
must remain on beta 3: stable beta-2-based code does not read its chip-bound
correction. Beta 3 and firmware-beta remain prereleases. The local recovery cache
is deliberately still beta 3; the stable recovery set is separately held under
.tools/stable-release/recovery-cache. Do not accidentally downgrade the corrected
unit while changing recovery targets. This promotion adds no physical acceptance
evidence; earlier coverage limits remain.

## Chip-bound divider correction — beta 3, 24 October 2026

Beta 3 adds a USB-only, checksummed, chip-bound NVS multiplier for divider sensing.
The normal multiplier is 1.000; a supplied 1.790 correction was provisioned only
on the currently verified C3. The base 1.0135 calibration, startup thresholds and
400 mA computer USB ceiling are unchanged. User backup/restore/reset does not
transfer/remove unit hardware calibration. Generic S3/C3 images contain no unit
identity or calibration profile.

Software: 51 Python tests and 16 native suites pass. Native tests verify identity
mismatch/corruption rejection and actual startup behaviour: the corrected divider
passes at 400 mA, while a different chip retains default calibration and fails
that same wrong-divider simulation. Both pinned cached-dependency builds pass;
final images S3 1,368,144 bytes, C3 1,411,440 bytes, within OTA slots.

Physical: after fresh USB-only power confirmation, ROM identified the current C3.
Its prior beta 2 status reported invalid divider reading and 0 mA. The two-slot
layout and VALID app0 were checked; only app0 was rewritten. Partition table,
NVS and OTA metadata matched byte-for-byte before/after application upload.
Then the USB command stored 1.790 bound to the live eFuse ID. After reset, status
confirmed persistence, 5.083 V reported startup voltage, VALID firmware, ready
library and 400 mA USB ceiling. Profile/custom counts and generation matched the
baseline. This is not an independent meter measurement or external-supply test.
Private identities, flash/NVS and serial records remain ignored local output.

## Automatic USB batches restored — 24 October 2026

Recover Dragon.cmd now retains manual recovery and adds opt-in automatic batches.
One USB-only confirmation enables the batch. Each native Espressif USB connection
is read for its running version, identified from ROM and updated only when older;
same/newer versions skip writes and undergo startup verification. Responsive
unversioned legacy firmware uses recovery; unreadable/unrecognised firmware stops
Auto. Two absent scans plus a settling period gate the next board so USB
re-enumeration cannot trigger another write. Multiple boards or any error stop
Auto. STARTUP PASS is firmware/storage/uptime/power/OTA validation, not an LED or
sensor test. The prepared S3/C3 firmware remains beta 2; no rebuild or firmware
publication is needed for this host-only correction.

51 Python tests pass, including simulated ROM identification, version
ordering/no-write paths, disconnect/re-enumeration, power confirmation and real
Tk worker flow. The real local recovery window passes preflight with both cached
beta 2 images and the standalone tool. No connected board was probed or flashed
during this correction; physical batch acceptance remains pending.

## Visible firmware and prepared recovery — beta 2, 24 October 2026

`v0.3.0-beta.2` shows actual installed firmware and board type on the main page,
without unlocking Parent settings. Device state and serial status expose the same
compiled tag. Recovery now prefers installed standalone esptool, verifies both
board image headers as well as bundle hashes/layouts, shows the prepared version,
and waits for expected firmware plus VALID startup before reporting success.
Per-board power confirmation resets after each operation; startup-only retry does
not rewrite flash. Both S3/C3 beta 2 bundles are prepared in the local recovery cache.

43 Python tests, 16 native suites and browser simulations pass; both targets
compile/link with pinned cached dependencies (clean Arduino CLI remains blocked
by Windows Application Control). Final images: S3 1,367,040 bytes, C3 1,409,952
bytes, both within the slots. Real RSA signatures and packaged hashes/layouts
were checked. The actual recovery GUI preflight succeeds using the local runtime,
new bundle and installed standalone tool. This is software/readiness evidence:
no additional board was probed/flashed, and C3 physical acceptance remains open.

## Beta update channel and Glitter contrast — 24 October 2026

The `v0.3.0-beta.1` release adds a 10% silhouette for the Glitter button while white
wing sparkle peaks retain the existing 80% channel ceiling. Session power, ambient
and user gains still apply. Native tests check contrast and all current budgets.
Release is the default update channel; Beta is an explicit parent choice with a
USB recovery notice. Device handlers validate channel selection, use separate
manifest locations and reject beta metadata in Release. Signed immutable release
assets are selected through the `firmware-beta` prerelease pointer. Ordinary users
will not receive this beta through Release. Older candidate firmware needs one
file upload to gain the channel selector. Browser simulations cover board labels,
beta selection and return to Release on locking. Software checks pass: 39 Python tests, 16 native suites and browser simulations.
Both targets compile/link with cached pinned dependencies (clean Arduino CLI is
blocked by Windows Application Control). Final signed beta images are S3
1,366,384 bytes and C3 1,409,360 bytes, within 1,572,864-byte slots. RSA signatures
were independently verified after packaging; the recovery bundle passed layout
and checksum validation. No new physical pass is claimed.

## Board-specific update guidance — 24 October 2026

The parent firmware panel reads the protected board API after unlocking and names
ESP32-S3 or ESP32-C3 with the exact matching `dragon-s3.dragon.json` or
`dragon-c3.dragon.json` download. Direct updates select the target automatically.
File upload still checks the device target before starting, with a specific
wrong-board message. Browser simulations cover both labels; both targets compile
and link using the cached pinned dependencies. The live device at its home-network
address reports S3. The new guidance is packaged for user upload testing; it has
not yet been installed or physically verified. No GitHub release was published.

## Simplified parent access — 24 October 2026

Latest user decision: parent access is a deliberate settings action using the
fixed shared password `dragon123`. No password change or USB setup code is needed.
The parent area shows only its password form until accepted; settings are hidden
and inert while locked. Existing sessions and independent firmware API checks
remain. Lock, reload, expiry and rejected tokens hide the controls again. The
old password-change route is retired, and saved custom parent credentials are
ignored. This supersedes USB-code/password-setup instructions in earlier entries.

Software checks pass: 39 Python tests, 16 native suites and phone-sized browser
simulations including fixed login, wrong-password rejection, hidden controls,
locking and expiry. Setup Wi-Fi is explicitly described as having no internet:
users download offline files before joining it, and direct checks remain disabled
until home Wi-Fi is connected and setup Wi-Fi closes. Both targets compile/link
with cached pinned dependencies. The S3 update was installed over USB without
changing partition table, NVS or OTA metadata. Updated app0 validated, with
two creations/generation 14 and the 400 mA ceiling intact; physical evidence is
recorded separately. A local HTTP upload attempt interrupted at roughly 67% left the
previous app0 VALID and saved data intact. No complete web OTA or rollback pass
is claimed.


## Direct online updates and physical S3 migration — 24 October 2026

The parent page now offers Check for updates, explicit installation approval,
progress and cancellation. A background HTTPS task downloads bounded signed release
metadata and the board-specific binary from GitHub; the main loop retains OTA and
lighting ownership. The pinned CA bundle, hostname checks, HTTPS-only release-host
redirects, signed board/tag/size/hash metadata and complete image verification are
required. File uploads still work offline. No online release assets have been
published during this work; old releases without a manifest return a clear message.

Software checks: 39 Python tests, 16 native suites and phone-sized browser
simulations passed. Actual online route handlers are tested with deterministic
network/crypto adapters for authentication, signed-check-before-erase, wrong board,
parent-approved install, progress and expiry cancellation. Separate Python tests
use real RSA signatures including tag tampering. Both boards compile/link with
cached pinned dependencies; generated images are S3 1,364,064 bytes and C3
1,407,216 bytes, within the 1,572,864-byte slots. Clean CLI builds remain blocked
by Windows Application Control. The installed standalone esptool runs normally;
recovery can explicitly select it with `--esptool` without changing Windows policy.

Physical evidence is recorded separately in the [24 October S3 record](HARDWARE-TEST-2026-10-24.md).
After explicit USB-only power confirmation and ROM identity verification, the S3
was migrated to two slots. A complete original flash backup is preserved privately;
NVS matched byte-for-byte across migration and against that original backup.
Two creations, All and generation 14 survived, with the 400 mA USB ceiling intact.
Startup confirmed app0 VALID. Saved home Wi-Fi did not join (reason 210); the bounded
attempt stopped and AP remained active through about 158 seconds uptime.

Windows initially denied WLAN access. After the user enabled Location services,
access succeeded without elevation. The laptop joined the real AP: the embedded
page and ordinary APIs worked without login, all 16 tested sensitive routes
returned HTTP 401 without parent credentials, and headless Edge confirmed automatic
clock sync against the actual device. The previous laptop network was restored
and the temporary profile removed. This is live desktop/device evidence, not
physical phone coverage. Home Wi-Fi did not connect, so actual online firmware
installation remains unverified.
No signed GitHub assets were published. Physical rollback/interruption, real-phone
setup/channel handover and the C3 remain open gates. The earlier software-source
checkpoint below retains its historical scope before this physical session.


## Next firmware release source — 24 October 2026

The [0.3.0 candidate](NEXT-RELEASE.md) implements the latest product direction:
login-free ordinary controls; device-enforced parent sessions for Wi-Fi, backup,
restore, updates, reset and credentials; AP at every startup; one bounded saved
home-network attempt; explicit retry; AP shutdown after successful join; no automatic
AP reopening after a later drop; no setup touch hold/purple cue. Automatic phone
clock sync is visibly confirmed. Collection rotation pauses for sleep/sunrise.
Signed offline updates use two slots and defer startup validation/rollback.
Backups use validated snapshots and an interrupted-restore redo journal.

First parent credential setup/recovery uses a USB-generated ten-minute one-use code,
separate from the unchanged AP password. The [single-device recovery tool](USB-RECOVERY.md)
backs up and verifies unchanged NVS around a board-matched migration. Existing
manufacturing tooling and previous local release bundles are retained separately.
Only the public update verification key is source-controlled. Keep the private
signing key in ignored local storage and back it up privately before distribution.

Software evidence (not physical): 38 Python tests, 16 native suites and the updated
390x844 browser workflow pass. Native tests execute the actual parent, update and
backup routes with deterministic crypto/flash adapters, covering auth rejection,
invalid/wrong-board manifests before erase, interrupted/incomplete/tampered uploads,
session expiry and restore-journal retry. Separate Python tests use real RSA signing
and verification and simulated NVS-preserving USB writes. Existing wing-isolation,
All/membership, saved-data migration and 400 mA USB ceiling regressions remain.

Both pinned board compilers accept the real translation unit; linking succeeds
against cached pinned dependencies. ELF inspection confirms a strong C-linkage
`verifyRollbackLater` symbol. Application images are 1,179,664 bytes (S3) and 1,206,880 bytes (C3),
within the 1,572,864-byte slots. Signed candidate packages and checksum-verified
recovery bundles are isolated under ignored `.tools/next-release/` and
`.tools/recovery-release/`. Clean
Arduino CLI builds are blocked by Windows Application Control (WinError 4551)
on this machine, so direct compiler/link/image checks are recorded separately.
Candidate images, signatures, private key and logs remain ignored local outputs.

No port was probed and no device was flashed in this session. Actual iPhone/Android,
radio-channel association/handover, AP shutdown, later disconnect, power-cycle
recovery, interrupted physical updates/rollback, NVS preservation across migration,
restore interruption and USB recovery remain mandatory physical gates on both boards.
Earlier physical evidence below applies to the earlier installed release only.
Supplied hardware files and power safety policy are unchanged.


## Printable setup cards published — 24 October 2026

The existing universal A5 setup card and A4 rear-label sheet are now tracked in
`output/setup/`, with download links in README and the [print guide](QR-SETUP.md).
Only these two PDFs are exempted from the output ignore rule. Personalised cards,
credentials, visual-review renders and the local Pages checkout remain ignored.
The PDFs are unchanged from the previously reviewed universal-card edition;
printed phone scanning and enclosure fit remain pending.

## Hardware files received — 23 October 2026

The native Fusion design archive `NightLamp.f3d` was subsequently added to the
same intake, with its attachment checksum verified. The package now contains
nine supplied files. Fusion component coverage and external dependencies have
not been checked; receipt does not establish fabrication completeness.

The user supplied six STL files, a BOM workbook and a Gerber ZIP, now preserved
in [the dated hardware intake](../dragon-firmware/hardware/supplied-2026-10-23/README.md).
All eight files match the supplied attachments by SHA-256. Original filenames
and bytes are retained, including the September dates on the PCB files.
This supersedes earlier statements that those files were pending. Build photos
remain pending; design review, units/orientation and physical-fit validation
have not been performed during this publication. These files are not labelled
as an approved final design. Firmware and physical-test evidence are unchanged.

## GitHub checkpoint — 23 October 2026

This checkpoint preserves the current source, batch-flasher Auto mode,
universal QR setup workflow and manual edition 0.7. All 34 Python regression
tests passed again before publication. No board was connected or flashed for
this publication; previous physical evidence retains its recorded scope.

The user will supply newer STL and Gerber files soon. Those files and build
photos remain pending; existing mechanical and PCB assets are earlier prototypes,
not the final design. The `keeper-edition-draft/` folder is retained as an
archival design draft; active sources remain in `dragon-firmware/web/` and `docs/`.

## Universal QR setup — 20 October 2026

[Universal cards and rear labels](QR-SETUP.md) now use the same two QR codes for
all dragons: the public manual and the local setup controls. The A5 card has an
optional handwritten Wi-Fi-name blank. No personalised printing or serial capture
is required. Sources generate ignored `output/setup/` PDFs without a board.
Manual edition 0.7 and parent/setup guides describe the shared-card workflow.
All 14 rendered QR codes decoded correctly; card, labels and eight manual pages
were visually reviewed. Printed phone scanning and enclosure fit remain pending.
The manual QR now points directly to the edition 0.7 PDF on GitHub Pages at
`https://sai021.github.io/dragon-kingdom/manual.pdf`, served from `gh-pages`.
It opens without an intervening webpage; browser settings determine viewing
or saving. Regenerated cards supersede the earlier Markdown-link cards.
Firmware and physical-test evidence are unchanged.

## Batch flasher Auto mode — 20 October 2026

`Flash Dragons.cmd` now offers an opt-in **Auto mode — flash on connection**.
It uses the existing ROM chip detection, matching checksum-verified S3/C3 image,
upload and startup check. After each operation it waits for confirmed unplugging
before accepting the next board, including when USB changes COM numbers.
Ambiguous connections or operation/discovery errors switch Auto off. Disabling
Auto during an operation lets it finish; opening the app always starts in manual
mode. See [batch flashing](BATCH-FLASHING.md) for the swap sequence.

Software evidence: all 34 Python tests passed, including 21 flasher tests and
nine new real-Tk tests
with simulated discovery, upload and startup responses. No hardware was probed
or flashed for this change; physical Auto-mode batch verification is pending.
Firmware sources, saved data handling and power limits are unchanged.

## Firmware checkpoint

Latest: [keeper edition 0.2.4](KEEPER-EDITION-2026-10-19.md), with a dragon-only
editor, fixed favourites search, manual edition 0.6 and user-confirmed enclosure
layout. Both firmware targets are rebuilt; the updated C3 image is installed
and its embedded web workflows checked. The 0.2.3 physical history follows.

The latest [Dragon Kingdom release](KINGDOM-RELEASE-2026-10-19.md) includes the
renamed interface/assets/manual, all accumulated improvements and separate
checksum-verified S3/C3 firmware downloads. Both published 0.2.3 images are now
installed and physically checked under laptop USB-only power.

The [radio readiness repair and latest hardware results](WIFI-READINESS-2026-10-19.md)
verify the intended 8.5 dBm driver setting and 400 mA USB ceiling. S3 passed five
ROM-only reset/HTTP trials in a clearer antenna position (7.4–8.6 seconds),
plus a user-operated cold USB boot/HTTP check at about 7.6 seconds uptime.
Earlier S3 reconnect failures and an unexplained helper/reset error remain
unresolved; these later passes do not prove their cause or broader reliability.

C3 0.2.3 passed preserved-library startup, saved-home-Wi-Fi connection, five
reset/HTTP trials (7.3–8.6 seconds) and the actual embedded web workflows.
Its final cold USB boot reconnected at about 7.6 seconds uptime; the user
confirmed normal lighting, tap, double-tap, hold and LDR response, with matching
telemetry. Earlier C3 0.2.2
normal/held cold boot, setup Wi-Fi visibility and physical gestures/sensors
passed with user confirmation and telemetry. Detailed dated evidence remains
in the [physical record](HARDWARE-TEST-2026-10-19.md).

The remaining gates include deployed external supply/current/thermal behaviour,
final prints/PCB/optical fit, physical phone browser coverage, range and endurance.
Earlier prototype assets are not the final design. The sections below retain
the earlier software and test checkpoints.

The [19 October reliability repairs](RELIABILITY-FIXES-2026-10-19.md) are the
earlier software checkpoint: 25 Python tests, 15 native suites, expanded browser
simulations and both firmware builds passed. The saved S3/C3 pair is prepared;
no board was flashed during the repairs. The intended product has one child,
with optional favourite collections.

Documentation was updated after those repairs. The [user manual](USER-MANUAL.md)
and [printable PDF](../output/pdf/dragon-kingdom-user-manual.pdf) are edition 0.6 (keeper edition),
19 October 2026, covering busy controls, alarm recovery and interrupted saves.
The software images and earlier physical evidence retain their recorded hashes.

Documentation verification on 19 October: the manual was regenerated and all
eight rendered A4 pages were visually reviewed. Edition/date and every page
number were checked from the finished PDF. All 62 local file links across the
26 root, project and firmware guides resolved. Parent, setup, collections,
development and flashing guidance now describe the repaired behaviour. These
are documentation checks; no hardware was connected or firmware installed.

For the next live session, start with [Testing handover](TESTING-HANDOVER.md): final
device state, completed evidence, local tool/evidence locations and the remaining
live web-service checks. It is the current testing checkpoint.

The [release checkpoint](RELEASE-CHECKPOINT-2026-10-18.md) consolidates the
historical software builds, documentation and remaining release gates. Resumed
live desktop UI tests passed glow, sleep/wake, alarm preview/stop and save/reload,
Wi-Fi scanning, and temporary profile/custom/favourite saves. The user confirmed
that the original network isolates devices; the laptop reached the dragon after
joining a network that permits local communication. All test objects were removed
and All / Blue / 100% glow / disabled 07:00, 20-minute alarm restored.

The dated sections below retain earlier implementation and test history.
Earlier software-only statements do not supersede the subsequent physical
session or its final results. Detailed evidence is in the linked test records.

## Character-colour audit — 18 October 2026

[All 81 stored slots were reviewed](COLOUR-AUDIT-2026-10-18.md). The source CSV
itself contains inaccurate colours and tribe/name errors, rather than evidence
of a wholesale index swap. Corrected palettes use documented colour families
with approximate RGBs and sparse 8x8 markings. Belinda and Ladybug are retired
from selection, leaving 79 selectable presets while retaining all IDs/order and
custom-base compatibility. Existing retired favourites are filtered after valid
snapshot loading. Physical colour/optical confirmation remains outstanding.

## Whole-wing sunrise and brighter glitter — 18 October 2026

Six bottom pixels previously classified as background now belong to left/right
wing interiors. All 37 wing pixels (13 left interior, 16 right interior, eight
edges) participate in sunrise; the 27 face/body/horn/tail pixels remain excluded.
The editor hides the unused background region while retaining its stored ID for
compatibility. Existing per-pixel palette colours and library schemas remain
intact; legacy background-only overrides have no physical pixels after remapping.
Glitter now adds light instead of blending away bright channels. The play-button
glitter uses white sparkles with a longer peak, higher density and wing edges.
All channel, ambient, touch and session-power limits remain in force.

Software/build and installation evidence is recorded in the testing handover.
The earlier checkpoint below describes the previous images. Physical appearance
and bottom-wing coverage need user confirmation after installation.

## Physical S3 session — 18 October 2026

See [the hardware test record](HARDWARE-TEST-2026-10-18.md) for the real USB-only
session, separately from native/browser simulations. ROM identity, upload,
400 mA USB ceiling, startup ADC readings, visible colour/effect sequence, LDR
response, physical tap and the on-device sunrise preview were exercised. The
user confirmed the colour sequence, physical tap and replayed sunrise. Direct
setup Wi-Fi with Pixel USB tethering enabled real embedded-page, clock-sync and
brightness checks. Phone hotspot peer isolation is suspected. A real scheduled
sunrise reached 100%; its saved schedule and network credentials survived reset.
USB recovery reopened setup Wi-Fi and saved the alarm disabled. The Slate Plus
router subsequently connected after limiting ESP32 TX power to 8.5 dBm. Real
router-side HTTP controls and automatic reconnection after reset passed; a
temporary profile, custom dragon and disabled alarm survived reset, then test
objects were removed and original lighting/alarm settings restored. A stale
timer-sample bug that immediately cancelled new joins/closed setup Wi-Fi was
fixed, with rollover/future-timestamp regression coverage. A two-metre Slate
check passed 24 HTTP samples spanning the move and restart reconnection; the original house network also joined. One switch crash was
observed without its original stack trace. The mDNS teardown order was corrected;
four subsequent logged network switches passed HTTP checks without a panic or
uptime reversal. A final restart rejoined the saved house network in about
9.1 seconds, followed by ten successful HTTP samples and brightness control.
The alarm is off and original lighting restored. Broader coverage, longer
reliability, NTP recovery after a power cut and independent electrical/optical
checks remain outstanding. USB diagnostics and a hidden-password provisioning helper
were added; the batch startup checker now enables DTR without pulsing RTS.

## S3/C3 firmware and batch flasher — 18 October 2026

The device setup Wi-Fi and browser password is now the shared `dragon123`
(browser username `parent`). Updating replaces older random access keys on boot;
saved home-network credentials and library records are preserved. Existing setup
cards must be updated. This deliberately trades unique device passwords for
easy entry; reachable users who know the password can change settings.

An optional ESP32-C3 SuperMini build now maps the supplied eight power-side
header positions to GPIO3 matrix data, GPIO2 TTP223, GPIO1 voltage ADC and
GPIO0 LDR ADC. S3 assignments remain unchanged. Both retain hardware USB CDC,
the 400 mA estimated computer-USB ceiling, network-event locking, partition
offsets and saved-data migration behaviour. C3 uses 4 MB flash/DIO without PSRAM.

The batch flasher builds and saves separate checksum-verified S3/C3 bundles,
probes the selected chip with esptool before upload, and selects the matching
bundle. Detection failures, unsupported chips and invalid/missing bundles block
writing. Serial startup verification now also requires the computer-USB ceiling
and a reported session limit no greater than 400 mA (zero is allowed on a bare
board without the voltage divider).

Software evidence: all 17 Python tests and eleven native C++ suites passed,
including simulated C3 pin selection, USB detection and session limiting.
Flasher initialization passed with serial discovery disabled; no board was
probed or flashed in that check. The C3 Arduino build passed at 1,139,328 bytes
of app storage and 41,872 bytes of static RAM, within the custom app partition.
The S3 Arduino build also passed at 1,117,838 bytes and 50,908 bytes of static
RAM. Both images were saved as separate local batch bundles and their manifest
checksums rechecked. No hardware upload or live chip-detection test was performed.

Physical C3 evidence is outstanding: confirm actual footprint/orientation,
GPIO2 strapping with TTP223 idle/held at cold boot and setup recovery, voltage
ADC calibration against a meter, LDR, matrix, USB detection, Wi-Fi and saved-data
workflows. Software success does not approve the carrier fit or C3 hardware.
Keep laptop USB and external/main power mutually exclusive.

Batch-build responsiveness fix: an observed build was still running compiler
processes while nonverbose Arduino CLI output remained silent. The flasher now
streams verbose output, shows target/elapsed time and an activity bar, drains
bounded event batches, and reuses per-target workspaces. Published bundles remain
separate; an OS-released build lock prevents concurrent updated-flasher builds.
All twelve flasher tests passed, including a real Tk event-loop test with
simulated compiler success/failure, workspace reuse and saved-image preservation.
This check does not constitute a hardware flash or a new firmware runtime test.

## Full matrix palettes and horizontal orientation — 18 October 2026

Audited all 81 supplied dragons: each had six black BG pixels and 58 coloured
pixels. The editable catalog now fills those six pixels with that dragon's wing
colour, keeping the other pixel colours, catalog IDs/order and region allocation.
The original imported CSV remains a historical source; reimporting it replaces
these catalog edits. Custom creations can still explicitly select black.

Default output wiring now mirrors horizontally in response to the user's observed
left/right reversal. This applies consistently to palettes and region edits;
no saved-data schema or physical optical-mask allocation was changed.

Software evidence: 20 Python tests and all eleven native C++ suites passed,
including all 81 full-pixel palettes, horizontal mapping, animation current caps,
profile persistence and the C3 USB ceiling. The S3 Arduino build passed at
1,117,838 bytes of app storage and 50,908 bytes of static RAM.
Physical orientation and optical fit
remain to be checked after upload; no board was flashed for this change.

## Implemented

### Daylight glow and daily sunrise alarm — 18 October 2026

Bright daylight now keeps 100% ambient gain rather than shutting LEDs off.
Dark-room dimming, explicit sleep and all power ceilings remain intact.
The phone page adds a saved daily wake-up time, adjustable 1-120 minute sunrise,
30-second preview and stop control. Wing interiors/edges fade orange to warm
white independently of ambient/manual sleep, hold for 30 minutes, then return
to previous lighting. Touch/play controls dismiss the active sunrise.

Alarm settings and phone timezone/DST rules use a separate checksummed
`dragon-alarm/settings` record. Existing Wi-Fi/library records and migration
are unchanged. UTC comes from phone sync or optional NTP. Offline restarts need
the page opened again because no battery-backed RTC is present. Rules cover
400 days; an expired/invalid clock waits for sync. DST gaps skip nonexistent
times and repeated times fire once. The active ramp uses monotonic elapsed time.

Software evidence: 20 Python tests and twelve native suites passed, including
daily/midnight/DST timing, clock loss, cancellation, failed/corrupted persistence,
preview rollover, wing isolation and all startup current ceilings. A 390x844
browser simulation passed saving/reload, preview/stop, failed-save feedback,
clock-sync payloads and preservation of draft fields while polling, alongside
existing phone workflows. The seven-page user manual was regenerated and all
pages visually checked. Physical alarm timing, LDR behavior, real phone/NTP
sync, sunrise colours and optical wing isolation remain to be validated after
upload. No board was flashed for this change.

Both Arduino builds passed within the 1,572,864-byte custom app partition:
S3 1,143,278 bytes / 51,172 bytes static RAM; C3 1,166,226 bytes / 42,128 bytes
static RAM. Separate saved batch-flasher images were refreshed and their
checksums reverified. These are software build results, not physical evidence.

Touch control, 81 supplied palettes, local phone controls, Wi-Fi provisioning,
setup recovery, protected All, three named profiles, ordered favourites,
per-profile play lists, eight custom creations, region editing/effects,
creation copying/deletion, profile deletion with retained creations, ambient
dimming and startup power diagnostics are implemented.

An earlier installed build was 1,117,518 bytes with 50,908 bytes static RAM.
Those historical figures are superseded by the final network-switch build
and the release checkpoint linked above.

## Evidence

| Area | Evidence and limit |
| --- | --- |
| Supplied catalog | Existing Python import/config/editor checks passed |
| Firmware core | Native C++ suites cover layout, power, effects, sensors, startup and connection timing |
| Library | Native tests cover ownership/membership, region overrides, save/reload, checksum fallback, failed writes, deletion and protected All |
| Custom rendering | Maximum-white creations remain capped across six effects and six power ceilings; empty-profile touch isolation checked |
| Phone workflows | Headless 390×844 browser checks with simulated API responses passed play, Wi-Fi, editing, filtering and deletion flows |
| Wired prototype | USB startup windows passed at about 5.11 V; 400 mA estimated ceiling remained active; no observed panic after the fixes |
| Latest migration | Live Family became All, retaining one custom creation and generation 8 after upload |
| User feedback | User confirmed profile creation and identified the collection-filtering/deletion changes incorporated in this checkpoint |

Browser simulations do not verify the real ESP32 HTTP/NVS stack. Brief live
uptime observations do not constitute a long-duration reliability test.

## Before a family trial

1. Verify actual iPhone and Android setup, authentication, Wi-Fi scanning,
   wrong-password retry and reconnecting through home Wi-Fi.
2. Save a profile/creation through a phone; unplug/replug and verify persistence.
   Test profile deletion, shared favourites and preserved creations in All.
3. Verify the TTP223 power-on setup gesture on the actual assembled product.
4. Exercise touch while web requests and saves are in progress.
5. Measure Wi-Fi supply behaviour and validate the provisional controller budget.
6. Test the deployed supply with laptop USB disconnected, including sustained
   brightness and the intended cable. No runtime voltage sampling exists.
7. Prepare per-device setup cards; implement lost-card/reset recovery and
   parent settings protection before unsupervised distribution.

## Hardware and mechanical status

The September PCB/CAD and optical files are earlier prototypes, not the final
manufacturing release. The 21 September Gerber review retains a required R4
pad-entry routing correction and outstanding native DRC/physical-fit checks.
See its original review rather than interpreting a preview as manufacturing
approval.

The user is printing newer STL files. New meshes, making-of photographs and
updated/final Gerbers will be supplied later. They are not present in this
checkpoint and must not be inferred from the older files.

Firmware and older optical masks use different pixel-to-zone allocations.
Reconcile them against the final physical design before claiming calibrated
colour isolation. This checkpoint deliberately preserves each source.

## Development backlog

| Priority | Work |
| --- | --- |
| Next | Physical phone/persistence tests; incorporate user's finished print/CAD/photos/Gerbers |
| Before family release | Parent protection, lost-card recovery, power measurements, final assembly validation |
| Next feature | Export/import profile and creation backups with schema migration |
| Optional | Weather dragon mode, selected town/postcode, cached data and offline fallback |
| Later | Firmware update strategy, product instructions and longer reliability testing |

Weather, cloud accounts, remote control, voice/audio and OTA are not implemented.
