Software and documentation follow-up - 19 October 2026

Latest: [Dragon Kingdom release verification](KINGDOM-RELEASE-2026-10-19.md).
The renamed S3/C3 pair supersedes the prepared images below. Setup Wi-Fi and
mDNS change to `Dragon-Kingdom-XXXXXX`; saved data stays compatible. The S3 on
COM17 was ROM-identified and the 0.2.2 image installed under confirmed
USB-only power. See the [19 October physical record](HARDWARE-TEST-2026-10-19.md)
for live API/UI/persistence tests, touch/LDR evidence and the two fixes found.
The user confirmed tap/double-tap and that covered-LDR minimum glow stays lit.
A C3 was subsequently connected on the carrier (COM61), ROM-identified and
flashed with the published 0.2.2 C3 image. USB startup/library/400 mA checks passed;
visible lighting, gestures and LDR response also passed with user confirmation
and matching telemetry. Wi-Fi and cold-boot strapping checks are ongoing.
Repeated final reset tests exposed intermittent home-Wi-Fi reconnect failures.
Do not treat the earlier successful reconnect as proof this is resolved.

The [reliability repairs](RELIABILITY-FIXES-2026-10-19.md) are built and saved as
one verified S3/C3 release set. No board was flashed in that repair session;
installed-device state below describes the previous firmware. Verify present
port, power arrangement and live state before upload. The intended product is
for one child; profiles remain optional collections.

The current manual is edition 0.5, eight pages, dated 19 October 2026:
[editable text](USER-MANUAL.md) / [printable PDF](../output/pdf/dragon-kingdom-user-manual.pdf).
Its updates cover disabled waiting controls, alarm load/clock recovery, stale or
interrupted saves, and low-power touch-only fallback. Historical references to
edition 0.4 below record what was checked in the earlier physical session.

# Testing handover - 18 October 2026

This is the starting point for the next chat's live web-service testing. Read
`README.md`, `docs/PROJECT-STATUS.md`, root `AGENTS.md` and
`dragon-firmware/AGENTS.md` first. The dated
[hardware record](HARDWARE-TEST-2026-10-18.md) contains the sequence and evidence
boundaries; this document summarizes the final checkpoint.

## Latest prepared firmware — character-colour audit

All 81 stored slots reviewed; 79 remain selectable. Belinda/Ladybug are retired
without renumbering the catalog or shifting custom IDs. Corrected Cadelle,
Hemlock, Queen Moorhen and Typhoon identities/tribes and documented scale-colour
families are detailed in [the colour audit](COLOUR-AUDIT-2026-10-18.md).
The historical CSV is unchanged. Before-edit catalog backup remains ignored.
New current flasher bundles: `20261018-193146-colour-audit-s3` and
`20261018-193220-colour-audit-c3`. Compiler app/static RAM: S3
1,147,710 / 51,300 bytes; C3 1,171,742 / 42,256 bytes. Both bundle hashes verified.
These corrected-colour images have **not been uploaded**; the device still runs
the earlier wing/glitter image below. The user plans further colour-editor edits
after this correction. Build again after any such edits before flashing.
Physical character-colour agreement remains unverified.

## Last known device state

Latest update: the whole-wing/brighter-glitter S3 build was installed on COM17
after ROM chip detection and a live baseline capture. Startup passed with ready
library, increasing uptime and the 400 mA estimated USB ceiling. Live HTTP
verified 37 wing pixels and zero BG pixels, unchanged saved library/alarm, and
restored the user's pre-upload **All / Blister / 100% glow** selection. Alarm
remains disabled at 07:00 / 20 minutes. This supersedes the older Blue state
below. Appearance still needs user confirmation; API zone counts are not optical
evidence. C3 was built but not uploaded or physically tested.

Latest bundles: `20261018-185051-wing-glitter-s3` and
`20261018-185124-wing-glitter-c3`, selected by the usual current manifests.
Compiler app/static RAM: S3 1,147,414 / 51,300 bytes; C3 1,171,398 / 42,256 bytes.
All 23 Python tests, 13 native suites and simulated phone-browser checks passed.
Native sunrise tests now require every non-body-part pixel to be lit at full
sunrise for each usable power ceiling, and check excluded parts stay dark.
Glitter regressions cover additive highlights and current ceilings.
The seven-page manual was regenerated and visually checked after the change.
Local evidence: ignored `.tools/wing-glitter-20261018/` contains build/upload
logs, pre-upload serial status, baseline and post-upload HTTP snapshots.
The older source/hash checkpoint is retained as historical evidence.

- Assembled **ESP32-S3**, ROM-confirmed 4 MB flash and 2 MB PSRAM, last on COM17.
  Recheck the port and live state before any upload; do not assume it persists.
- Powered by laptop USB. The user explicitly disconnected external/main power.
  **Never connect both power sources simultaneously with this circuit.**
- Firmware reports `computer_usb_cap=1`, `session_max=400mA`, ready library and
  increasing uptime. This is an estimated ceiling, not a current measurement.
  Runtime voltage sampling remains stopped as designed.
- Last left connected to the saved house Wi-Fi. Read the current/last-known IP
  and hostname from ignored local `device-endpoint.json` below, then verify them.
  DHCP addresses can change. The computer reached its API through the Slate
  router route during the last check; it need not currently have that route.
- Browser login: **parent / dragon123**. Setup Wi-Fi also uses `dragon123`.
  This is the device access password, not the house-network password.
- Original logical state restored: **All profile, Blue dragon, 100% manual
  glow**, no test profiles or custom creations remaining. Ambient dimming still
  applies. Alarm **disabled**, stored wake time **07:00**, duration **20 minutes**.
- The in-app browser may still show the Slate Plus admin log page. That is the
  router interface, not Dragon Kingdom. Do not assume its login/tab survives a new chat.

## What has passed

| Evidence | Result and limit |
| --- | --- |
| Physical S3 startup/upload | ROM identity, upload, startup ADC about 5.03-5.09 V, USB ceiling and ready library. ADC readings were not checked against a meter. |
| User-observed lighting | Orange, blue, glitter, off and restored blue sequence confirmed. Sunrise replay confirmed gradual wing brightening and return to normal. Precise optical isolation was not measured. |
| Physical sensors | User covered/uncovered LDR; serial values/gain changed. A physical touch advanced the dragon, confirmed by the user. Calibration retained. |
| Live embedded page | Headless Edge loaded the actual device over direct setup Wi-Fi at mobile viewport width; screenshot inspected, clock sync and brightness control passed without page errors. This was desktop rendering, not physical Safari/Chrome testing. |
| Daily sunrise | A real one-minute rise scheduled two minutes ahead started automatically and reached 100%, confirmed over HTTP/USB; stopped afterward. Preview was separately user-confirmed. |
| Live HTTP/API storage | Temporary profile, favourites, custom name/region colours and disabled alarm survived a serial-loader hardware reset. All-profile deletion returned 403. Test data was removed and original settings restored. |
| Slate Plus Wi-Fi | Full firmware connected and saved credentials at 8.5 dBm ESP32 TX power. Router logs independently confirmed DHCP. |
| Two-metre check | Two-minute monitor spanning the move: 24/24 HTTP checks passed. Signal settled around -58 to -62 dBm; reset/reconnection to HTTP took about 9.4 s. This is not a whole-house coverage test. |
| House Wi-Fi | Connected, saved and served authenticated HTTP. Final saved-network reset/reconnection took about 9.1 s; ten further HTTP samples over 30 s and brightness change/restore passed. |
| Network switching | Four logged USB-provisioned switches between house and Slate networks passed save-on-success and HTTP checks without a captured panic or uptime reversal after teardown reordering. Browser Wi-Fi form end-to-end is still to be tested. |
| Software regression | Latest source passed **23 Python tests and 13 native C++ suites**. Native tests and simulated browser responses are separate from the physical evidence above. |
| Builds/flasher | Final S3 app 1,147,250 bytes / static RAM 51,300 bytes; C3 app 1,171,166 bytes / static RAM 42,256 bytes. Both fit the 1,572,864-byte app partition. Separate saved bundles were refreshed and checksum-verified. **No physical C3 test.** |

## Firmware changes and caveats

- S3/C3 targets and ROM-based automatic flasher selection are implemented.
  C3 preserves the documented eight power-side header positions using GPIO3
  matrix, GPIO2 touch, GPIO1 voltage and GPIO0 LDR. This does not approve actual
  carrier fit, orientation or GPIO2 strapping behaviour.
- Daylight now retains ambient lighting instead of switching the dragon off.
  Sunrise settings/UI, daily scheduling, phone timezone/DST rules, preview and
  cancellation are implemented. There is no battery-backed RTC.
- `Config::WIFI_TX_QUARTER_DBM=34` caps Wi-Fi TX at **8.5 dBm** and is reapplied
  for station connections. The library-default-power Wi-Fi-only diagnostic
  failed; the lower-power diagnostic and full S3 firmware connected. This does
  **not** prove a supply or antenna fault. C3 radio and broader range are untested.
- A stale-clock bug was fixed: serial/HTTP handlers could create a timer later
  than the loop's sampled `now`; unsigned subtraction immediately expired a new
  join or reopened AP. Time is refreshed after handlers and short-deadline policy
  rejects future timestamps. Regression coverage retains genuine timer rollover.
- Join deadline is 60 s; late success saves pending credentials only when the
  connected SSID matches. The station is restarted before replacing its config,
  since the pinned library's disconnected-state `disconnect()` can be a no-op.
- **One house-network switch crash was observed; its original stack was lost.**
  mDNS teardown was then moved before station interface destruction, with redundant
  early disconnects removed. Four subsequent switches passed. This addresses a
  lifecycle hazard; it does not establish the original crash's root cause or
  prove long-duration reliability. Capture a full stack if it recurs.
- Keep `DragonPrototype/build_opt.h` network-event locking, the protected All
  profile, saved-data migration and the estimated USB ceiling intact.

## Next live web tests

### Resumed live browser session — 18 October 2026

The user reports that TWGH prevents devices talking to each other; moving the
laptop to Skynet restored access, also checked in the user's browser. Authenticated
reads of state, library, catalog and alarm passed at the saved numeric endpoint.
The initial baseline and final snapshot are in the ignored session directory as
`web-baseline-20261018-180512.json` and `resume-final.json`.

The actual embedded page was exercised in the in-app desktop browser: glow
40%/100%, sleep/wake, sunrise preview/stop, disabled alarm save at 07:05/21 minutes,
reload showing those values, and restoration to disabled 07:00/20 minutes passed.
Wi-Fi scanning displayed its busy state, completed, and re-enabled controls.
No network switch was submitted. All's rename field was disabled and its delete
control absent. A temporary empty profile disabled play controls; its custom
dragon with face glitter saved, appeared after reload, and a Blue favourite saved.
These are live desktop UI/API results, not physical phone or observed LED results.

One immediate sleep click following glow was ignored; a later click succeeded.
Source has a shared `commandBusy` guard that drops overlapping commands; this
needs a focused interaction review before declaring rapid controls covered.
Some UI updates took longer than the browser tool's default three-second wait.
The browser tool stalled on the profile-deletion confirmation, so UI deletion,
rehoming and custom-copy/delete remain unverified in this session. Cleanup used
authenticated API calls restricted to the two newly created test objects.
Final API verification shows only All, Blue at 100%, and alarm disabled at
07:00/20 minutes with no active preview. No firmware was built or uploaded.

Phone/desktop viewport comparison, physical phones, browser network switching,
error/recovery coverage and the remaining endurance/power checks below stay open.

1. Recheck USB-only power, serial port, actual endpoint and baseline state.
   Read `/api/state`, `/api/library`, `/api/dragons` and `/api/alarm`; preserve
   current user data and settings before introducing temporary test objects.
   Do not rebuild/flash just to rediscover a working endpoint.
2. Exercise the **actual embedded UI**: initial load/authentication, controls,
   polling/recovery, errors and repeated taps at desktop/mobile widths. Then
   coordinate physical iPhone Safari and Pixel Chrome checks with the user.
   `tools/test_web.cjs` uses simulated responses; passing it is not a live-device
   or physical-phone result.
3. Complete profile/favourite/custom-editor workflows through the UI: select,
   save/reload, copy/delete, ownership, empty profiles, All protection and
   profile-deletion rehoming. Verify region changes/effects on the actual LEDs
   where visual evidence matters. Remove only newly created test data afterward.
4. Test browser Wi-Fi scanning, busy/error states, save/reconnect, recovery and
   direct setup-AP flows. USB switching has passed; the browser form has not had
   the same complete end-to-end check. Coordinate network interruptions so the
   computer remains reachable. Restore the intended saved house network afterward.
5. Exercise the actual alarm form, clock sync, preview/stop, save/reload and
   cancellation by play/touch. Real daily scheduling and reset persistence have
   passed, while DST/midnight edge cases currently have native coverage only.
   Restore the alarm disabled at 07:00 / 20 minutes unless the user requests otherwise.
6. Longer sessions, router loss/recovery, broader coverage and cold-power-cut
   clock recovery/NTP remain open. A serial-loader reset does not prove NTP
   recovery after complete loss of power. External-only tests require disconnecting
   laptop USB first; deployed supply/current/optical/mechanical checks remain separate.

Record browser simulations, live HTTP, rendered desktop UI and user-observed
physical results separately. Do not declare the entire web service tested from
the successful API smoke checks.

## Local tools and private evidence

Workspace: `C:/Users/sai02/Downloads/dragon`. Shell: PowerShell.
Developer manual: [DEVELOPMENT.md](DEVELOPMENT.md). End-user manual:
[USER-MANUAL.md](USER-MANUAL.md) and `output/pdf/dragon-kingdom-user-manual.pdf`
(current edition 0.5, eight pages, 19 October 2026). Batch guide: [BATCH-FLASHING.md](BATCH-FLASHING.md).

Ignored session directory: `dragon-firmware/.tools/live-hardware-20261018/`.
Never copy its credentials, captures, diagnostic sources/binaries or NVS into
tracked documentation. Useful local files:

- `device-endpoint.json`: last successful endpoint/status, left on house network.
- `network-private.json`, `home-network-private.json`,
  `router-network-private.json`: current/house/test-router credentials. Read
  privately as needed; do not echo passwords or put them in command arguments.
- `nvs-before.bin`: pre-session NVS backup. Do not restore it casually: that
  would roll back saved data and network changes since the start of testing.
- `home-final-summary.json`, `home-final-startup.log`, `range-monitor.log`,
  `range-2m-startup.log`, `switch-summary.json`, `switch-*.log`: final evidence.
- `router-persistence.py`, `test-network-switches.py`, `live-browser.cjs`,
  `live-daily.cjs`: local diagnostic harnesses. Inspect before reusing; some use
  historical addresses, create temporary objects or change network/alarm state.

Native USB CDC needs **115200 baud, DTR=true, RTS=false**. Only one process
should own COM17 at a time. Safe diagnostics include `status`, `sensors`,
`wifi status`, `alarm status`; `wifi setup` reopens setup AP without erasing
credentials. `alarm stop` cancels the current occurrence; `alarm disable`
persists disabled state. `wifi sleep on/off` is a temporary runtime diagnostic.
Provisioning helper: `tools/provision_wifi.py --port PORT --credentials-file FILE`;
the credential file must remain ignored. The generic helper reports a detected
panic but can close before its full stack is collected; the local switch harness
adds raw capture and a short drain before closure.

Bundled Python:
`C:/Users/sai02/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe`.
Arduino CLI: `dragon-firmware/.tools/arduino-cli/arduino-cli.exe`.
Pinned core: ESP32 **3.2.1**. Build with `tools/dev.py build --board s3|c3 --cli PATH`
from the firmware folder. Run `tools/run_tests.py --zig PATH` using
`.tools/zig-windows-x86_64-0.13.0/zig.exe` there. See the developer manual for
portable setup; do not assume these local runtimes exist on another machine.

Final bundle manifests: `.tools/batch-flash/current.json` (S3) and
`current-c3.json` (C3), directories `20261018-175703-network-switch-s3` and
`20261018-175703-network-switch-c3`.
Use `flash_support.load_bundle()` to validate checksums and the correct target;
never select the S3 binary for a C3. Latest flashed image is the final S3 build.

The workspace has many modified/untracked files from this ongoing work and
earlier user work; there is no clean Git checkpoint implied by this handover.
Do not reset, clean, bulk-delete, commit or push them without the corresponding
user request. Edit web sources and `presets/dragons.json`, not generated headers.
New STL files, build photos and Gerbers are still expected from the user; existing
mechanical/PCB assets are earlier prototypes, not the final design.
