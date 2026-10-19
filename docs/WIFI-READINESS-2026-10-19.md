# S3 Wi-Fi readiness repair — 19 October 2026

The S3 reconnect follow-up found a race in applying the existing radio limit.
This record supersedes the earlier assumption that calling `setTxPower()` before
association necessarily applied the limit. It does not erase the earlier failed
trials or complete external-supply, range or endurance testing.

## Physical evidence and cause

The reconnected board was ROM-identified as S3 on COM17. USB status confirmed a
ready All library, zero customs, Blue, automatic light adjustment and the
400 mA computer-USB ceiling. A fresh baseline reset failed to join within
90.08 seconds. The current 20,480-byte NVS partition was backed up privately
before the diagnostic firmware installation; no whole-chip erase was used.

In the pinned Arduino ESP32 3.2.1 code, `enableSTA(true)` starts the driver but
does not wait for the asynchronous station-start event. `setTxPower()` rejects
calls until the station/AP started flag is set. The project ignored its return
value. A diagnostic image retaining that connection sequence reported
`tx_quarter_dbm=80 sta_started=1` while association failed, rather than the
configured `34`. These are driver maximum-power settings (20 and 8.5 dBm), not
measurements of RF output, USB current or supply voltage.

## Repair and verification

Connection startup now uses `WiFi.STA.begin(false)`, which waits for the station
start event without initiating association. It then applies the existing
8.5 dBm limit and checks success before calling `WiFi.begin()`. If applying the
limit fails, STA is stopped and the ordinary retry/error path is used. Saved
credentials, setup AP handling, network-event locking and library formats stay
intact. Serial `wifi status` now exposes the driver power setting and station
started flag so future tests can verify the assumption.

The repaired S3 image was installed with flash hash verification. Its first
trial reported `tx_quarter_dbm=34 sta_started=1`, joined home Wi-Fi and served
authenticated HTTP after 7.45 seconds of post-upload observation. The USB
ceiling remained 400 mA. The next reset also passed in 7.41 seconds, but the
following reset failed to join within 90.09 seconds despite the confirmed
34-quarter-dBm setting. The planned five-cycle run stopped at that failure.
The radio-setting race is repaired; it was not the only cause of the observed
reconnect failures. Home-Wi-Fi acceptance remains open.

Software checks passed: 25 Python tests, all 15 native suites, simulated browser
workflows in installed Edge, and both pinned S3/C3 Arduino builds. The browser
suite initially could not find Playwright's bundled browser; rerunning with the
installed Edge executable passed. These software checks are separate from the
physical S3 measurements. C3 physical tests earlier on this date apply to
v0.2.2; the subsequent updated C3 verification is recorded below.

Both v0.2.3 board archives are prepared with unchanged partition/storage layouts.
The paired source fingerprint is
`4c20fe7d4d16b924a49b54e342d2961e48a941ce924a926b80609bcee3dc2496`.

| Board | Application image bytes | Application SHA-256 |
|---|---:|---|
| S3 | 1,154,992 | `ceaf3b1eddc8932e7fe1534dccc9764d9c2b78544d574aef5885f7cd9f914a98` |
| C3 | 1,179,504 | `bb3c18307bf958fd6aa86aa771b3c7b2937a33193f21d351d83271e2f9858a80` |

Raw logs, saved settings, endpoints and release archives remain in ignored
`dragon-firmware/.tools/s3-reconnect-20261019/`. Never connect laptop USB and
external/main power simultaneously in this circuit.


A further trusted-USB join trial used the intended locally saved network
credentials with manual glow temporarily set to zero. No join was confirmed
within 90 seconds; normal 100% glow was restored in the cleanup path. This
trial does not support treating matrix load alone as the cause. Setup-AP
recovery and the S3 antenna/placement comparison are the next diagnostics.


Opening setup AP through USB was followed by a saved-home-network connection
99.91 seconds into the recovery observation. This is a successful recovery path,
not proof of causation. The actual 0.2.3 embedded page then passed authenticated
controls, alarm save/reload/restore and preview/stop, scan, protected All,
empty-profile reload, custom save/copy/delete, favourites and profile-deletion
rehoming in headless Edge. No page errors were captured. Temporary entries were
removed and original settings restored.

Final USB status at uptime 420–424 seconds confirms home Wi-Fi connected with
setup AP open, `tx_quarter_dbm=34 sta_started=1`, ready All, zero customs, Blue,
normal 100% glow, automatic dimming, disabled alarm, ready clock and the 400 mA
USB ceiling. The last disconnect reason remained 202 despite current connectivity.
Final RSSI was -79 dBm; the user was asked about antenna type and whether the
S3 occupied the same carrier/position as the successful C3. No antenna fault or
supply diagnosis is inferred from these observations.

All five GitHub CI jobs passed on the release-tag run for commit `6501b93`.
A separate main-branch run of the same commit timed out waiting for the simulated
initial alarm-error state (`test_web.cjs:139`); its failed browser job passed
on rerun, leaving all five jobs successful for main as well.
The local simulated checks and actual-device UI checks above passed separately.
Uploaded SHA-256 digests matched all five published release assets.


## Placement follow-up

The user confirmed an onboard antenna and moved the USB-powered S3 away from
the laptop with the antenna clear of nearby metal/bundled wiring. A 34-sample
continuous connection capture contained no disconnects and RSSI -65 to -53 dBm;
the first/last ten connected samples averaged -57.0/-53.8 dBm. Physical movement
preceded the user's acknowledgement by an unknown interval, so these windows
are not a precisely timed before/after experiment. The earlier final capture
had reported -79 dBm.

The first esptool reset attempt reported `Guru Meditation Error detected
(IllegalInstruction)` while connecting. A subsequent attempt identified the S3
but timed out writing the temporary flasher helper. A serial probe also stalled
on an unbounded write and was stopped. No firmware or flash write was attempted
in this placement session. The captured tool error has no firmware backtrace;
it remains a separate unexplained reset/USB observation, not a demonstrated
normal-running firmware crash or a passed reset trial.

A ROM-only reset (`--no-stub`) then succeeded. The unchanged 0.2.3 image joined
at about 8.6 seconds uptime with RSSI around -53 dBm and the intended radio
setting/USB ceiling intact. Subsequent reset tests use ROM-only identity/reset
commands to avoid uploading the helper. This changes the test procedure, so
placement alone is not established as the cause of any improvement.


All five ROM-only reset trials in the new position passed saved-network
reconnection and authenticated HTTP: 7.42, 8.58, 8.20, 8.56 and 7.44 seconds of
post-reset serial observation, with RSSI -51, -51, -53, -51 and -50 dBm. Each
confirmed the station-started flag, 8.5 dBm driver setting and the 400 mA USB
ceiling. The setup AP was not requested during these normal starts. This is
five successful trials under the changed placement/procedure, not proof of
reliability in the earlier position or longer endurance. A user-operated USB
power-off/on test is the next check; no source/binary was changed.


The user then unplugged USB for five seconds and reconnected the S3 in the new
position with touch untouched, confirming normal visible startup. The observer
captured an uptime reset and the home connection at approximately 7.6 seconds
uptime (the preceding status sample was 7,648 ms). Thirteen subsequent connected
samples were recorded through approximately 21 seconds uptime, with no panic
or backtrace marker captured. Post-boot authenticated state/library/alarm reads
passed. Final state is connected with setup AP closed, ready All, zero customs,
Blue, 100% manual glow with automatic ambient adjustment, original calibrated
LDR thresholds, disabled alarm, ready clock, 8.5 dBm driver setting and the
400 mA USB ceiling. RSSI was -53 dBm.

This completes five reset/HTTP trials plus one user-operated cold USB boot in
the clearer antenna position on v0.2.3. It does not prove the cause of earlier
failures, clear the unexplained helper/reset error, or establish range/endurance
or final-enclosure RF performance. The user was asked to reconnect C3 for a
physical check of its updated 0.2.3 radio-startup image; earlier C3 passes remain
0.2.2 evidence until that check is complete.


## C3 verification on the published 0.2.3 image

The user reconnected C3 on COM61 under the confirmed USB-only arrangement.
ROM identity was verified, its current 20,480-byte NVS partition backed up
privately, and the checksum-verified published C3 image installed with flash
hash verification and no whole-chip erase. The application SHA-256 is the C3
value in the table above. Before/after startup retained All, zero customs and
library generation 8. Startup passed the increasing-uptime/library/400 mA checks.
Saved home Wi-Fi reconnected and driver status confirmed 8.5 dBm and station
readiness.

Five ROM-only reset cycles each rejoined and served authenticated HTTP:
7.42, 7.45, 7.33, 8.50 and 8.56 seconds. RSSI at those connected samples was
-64, -66, -65, -64 and -65 dBm. Each retained the USB ceiling and radio setting.
The actual C3 embedded page in headless Edge then passed controls, sleep/wake,
alarm save/reload/restore and preview/stop, scan, protected All, empty-profile
reload, custom save/copy/delete, favourites and profile-deletion rehoming.
No page errors were captured. Temporary data was removed and original settings
restored. These are physical-device desktop-browser checks, not phone tests.
The final user-operated cold boot and touch/LDR results follow.
C3 evidence is in ignored `dragon-firmware/.tools/c3-final-20261019/`.


The user unplugged C3 USB for five seconds and reconnected with touch untouched,
then confirmed that lighting, tap, double-tap sleep/wake, hold brightness and
LDR cover/uncover all worked on 0.2.3. The observer captured one uptime reset
and home Wi-Fi connected at approximately 7.6 seconds uptime (preceding status
7,577 ms), followed by 62 connected samples. Post-boot telemetry recorded 11
touch presses, eight selected dragons, normal/sleep modes, brightness steps
0–10, LDR 575–2,074 (filtered 619–2,050) and ambient gain 10–50. No panic or
backtrace marker was captured during this observation.

Test selections/glow were restored through the normal authenticated API and
USB controls. Final USB and HTTP confirmed All/Blue/100% glow with automatic
ambient adjustment, zero customs, original uncalibrated C3 thresholds 600/3400,
disabled alarm, ready clock, home Wi-Fi connected, setup AP closed, 8.5 dBm
radio setting and the 400 mA ceiling. The last disconnect reason remained 202
while connected; no live failure is inferred from that retained field.
Both published 0.2.3 images now have physical startup, reconnect/HTTP and cold
USB boot evidence. No source or binary changed during these final checks.
The previously listed S3 anomalies and broader product acceptance limits remain.
