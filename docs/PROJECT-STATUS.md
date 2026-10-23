# Project checkpoint — 19 October 2026

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
