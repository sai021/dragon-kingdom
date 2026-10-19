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
v0.2.2; the updated C3 image is build-tested until physically installed again.

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
