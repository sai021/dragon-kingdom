# S3 physical test record — 19 October 2026

**Acceptance remains open: home-Wi-Fi reconnection after reset is intermittent.**
The latest installed image is 0.2.2, application SHA-256
`ae257d57571cb5e37065ef440b6a7fd5ad4482a0cb78ecbb6279ab5ba22b8ff1`.
The successful checks below must be read together with the failed restart trials.

The user confirmed **laptop USB power only, external/main power disconnected**,
with only an S3 available. ROM probing identified ESP32-S3 on the currently
enumerated COM17. The 0x9000–0xdfff NVS region was backed up privately before
updating. Neither upload erased that region. Flash writes were hash-verified.
The C3 build was not installed or physically tested.

## Installed images and findings

The initial Dragon Kingdom 0.2.0 S3 image booted with a ready library and the
400 mA estimated computer-USB ceiling. Saved home-network configuration, All and
alarm settings were retained. Initial Wi-Fi association did not complete within
the first 60-second attempt; automatic retry later connected. Subsequent reset
and the corrected-image installation reconnected and served authenticated HTTP.
This first delay remains recorded; this session does not establish its cause.

Live browser testing found that a saved custom copy could leave the old dragon
selected until the next polling refresh. Immediate edit/delete then opened the
old selection. Rendering had skipped selection updates because controls were
disabled during the save. The fix updates an available selection from the save's
authoritative state even while busy. The new browser regression fails against
the old code and passes with the fix.

The user reported that covering the LDR appeared to turn the matrix off at low
glow. A native reproduction confirmed that sequential integer scaling could
round an awake pixel to black at 10% ambient × 10% manual gain. Dimming now uses
the existing visibility-preserving scaler after the session power cap. It does
not light intentional black pixels or exceed their pre-dim values. Regression
checks cover 79 selectable presets at 300/400/500/800/1600/2400 mA budgets,
plus intentionally black output and the existing sleep tests.

The corrected **0.2.1 S3** image was then installed, with increasing uptime,
ready library and the 400 mA USB ceiling verified again. Its application SHA-256:
`b6d03d2cfbf049dd7b099b4c2ea186e7cbd17659db971042550b43cab50ec8ef`.

## Real device/API and browser checks

On the initial image, authenticated API checks verified branding, saved profiles
and alarm preservation, protected All, stale/missing request context rejection,
duplicate custom-save rejection, profile/favourites/custom creation, copying and
deletion, brightness changes and progressing sunrise preview/stop. A real reset
retained the temporary profile, favourite order, creation and disabled alarm;
home Wi-Fi reconnected. Deleting the temporary profile rehomed its creation to
All. Cleanup removed only the newly created test objects and restored the initial
All / Blister / 100% glow / disabled 07:00, 20-minute alarm configuration.

On the corrected 0.2.1 image, the actual embedded page was exercised in a real
headless Edge browser against the S3, using a 390 × 844 viewport:

- Authentication and new page title, glow 40%, sleep/wake and Wi-Fi scanning.
- Alarm save to disabled 07:05 / 21 minutes, reload and restoration to disabled
  07:00 / 20 minutes, preview and stop.
- Protected All controls; creating an empty profile and reloading it with play
  controls unavailable; creating a dragon with face glitter.
- Saving/reloading, immediate copy/edit/delete, favourite saving, profile
  deletion and creation rehoming to All, then custom deletion through the UI.
- No browser page errors. The test profiles/creations were removed. Original
  alarm fields were restored. A desktop-width render was also captured.

These are live-device desktop-browser results. A phone-sized browser viewport
does not constitute a physical iPhone/Android test or visual confirmation of
every LED region.

## HTTP transport and sensor evidence

Initial-image hardware HTTP tests passed fragmented authenticated requests,
incomplete-request timeout/recovery, oversized-header rejection, conflicting
Content-Length rejection and a client that did not read the page response.
Afterward, 100 state/library/alarm cycles completed (300 authenticated reads).
USB telemetry yielded 56 uptime samples, with no decrease or detected panic,
maximum status gap 1.109 seconds, and sunrise preview progress from 0 to 100%.
The longest three-read API cycle was 1.141 seconds. This is a short stress test,
not an endurance or free-heap measurement.

During the user's hands-on checks, a three-minute USB capture recorded 16 touch
presses, eight distinct selected dragons, awake/sleep modes and manual brightness
steps 0/50/70/90/100%. LDR raw readings ranged from 105 to 845, with automatic
steps 10–20%. This demonstrates live input and state changes. On the corrected
image at 10% manual glow, the user confirmed that covering the LDR kept the
matrix lit and confirmed tap/double-tap operation. They saw no brightness
change at that minimum; both dim levels can quantize to the retained minimal
LED output. This confirms the floor, not calibrated optical brightness.

The user then requested a stepped minimum-brightness test within the laptop USB
ceiling. With automation off, normal 10% manual glow was clearly visible. A
temporary serial `testglow` diagnostic was added to bypass both gain controls
and the visibility floor after the session cap, without saving settings.
At raw 10%, telemetry reached zero lit pixels/channel sum and the user confirmed
the matrix was off. Lower raw percentages were not run because output was
already zero. The comparison identifies the smallest retained nonzero LED
level as a usable minimum for this USB-powered pattern; it is not a calibrated
optical percentage or a minimum for a different supply/palette. The diagnostic
was ended and normal 100% glow/automatic dimming restored.

## Final restart failures and connection changes

A later reset retained the temporary verification profile/creation in USB status,
but HTTP did not reconnect within the test's 70-second window. A further recovery
capture also failed to connect. Logged disconnect reasons included 4, 8 and 202;
these are radio/association outcomes, not proof of the underlying electrical,
router or firmware cause. USB status continued with the 400 mA estimated ceiling
and no observed panic.

The initial STA start in `begin()` was removed because `connect()` immediately
stopped/restarted it. The next installation connected in 8.2 seconds, but the
following reset did not connect within 90 seconds. A temporary Wi-Fi sleep-off
diagnostic was accepted but did not establish a connection in its observation
window. The existing 8.5 dBm TX limit was then moved before `WiFi.begin()` so it
applies before association begins. That final installed image also failed its
90-second home-network test. Neither change is claimed to solve the failure.

The final image matches the paired release manifest's S3 application hash.
Saved configuration remains present. Further network/radio and supply evidence
is needed before closing the home-Wi-Fi acceptance gate.

The user clarified that the laptop and dragon use different Wi-Fi networks,
with a router rule permitting access. Programmatic Windows WLAN switching was
blocked by its Location permission setting; no successful laptop switch was
established, and internet connectivity remained available. Direct setup-AP
browser access therefore was not verified in that attempt.

Opening the dragon's recovery AP through USB was followed by a successful saved
home-network connection. Authenticated HTTP access through the router rule then
worked. All temporary verification profiles/creations were removed; the saved
profile list matched the baseline (only All), with zero custom test dragons.
The user's current Willow selection was restored at 100% normal glow, and the
alarm remained disabled at 07:00 / 20 minutes. A further image that disabled
Wi-Fi sleep before joining also failed its 90-second trial; that experimental
change was discarded. Recovery with AP open is evidence of an available path,
not proof of why ordinary station starts fail.

The checksum-verified canonical 0.2.2 image was reinstalled after discarding that
experiment. It passed USB startup/library/ceiling checks. Recovery AP opening
was reported, but the home network did not reconnect within the subsequent
130-second observation. Final USB verification shows protected All active,
zero custom test dragons, Willow at normal 100% glow with automatic dimming,
alarm disabled, and the 400 mA estimated ceiling. Home credentials remain saved
and the recovery AP is open; home-Wi-Fi readiness is not claimed. No final HTTP
stress rerun was possible in this state. Earlier transport metrics above apply
to the explicitly identified earlier image.

## Remaining physical limits

The later C3 follow-up below supersedes the initial lack of C3 hardware.
Deployed external supply/current/thermal behaviour, final prints and Gerbers,
optical separation/colour agreement,
physical phone platforms, deliberate router loss, cold power-cut/NTP recovery
and longer endurance remain separate checks. The old mechanical/PCB assets
remain prototypes. No simultaneous USB/external-power test was performed.

Raw captures, pre-update NVS, endpoints, logs and screenshots are kept under
ignored `dragon-firmware/.tools/kingdom-release-20261019/`. Do not publish them.


## C3 carrier follow-up

Later on 19 October, the user connected a C3 on the carrier and confirmed the
8-pin orientation (5V, GND, 3V3, GPIO4, GPIO3, GPIO2, GPIO1, GPIO0). Testing
continues under the previously confirmed laptop-USB-only power arrangement.
ROM detection identified ESP32-C3 on COM61; flash identification reported 4 MB.
The 20,480-byte NVS partition was backed up privately. A larger full-flash read
failed with a serial-stream error, and an application read timed out; neither
is claimed as a complete backup. The saved settings backup did succeed.

The checksum-verified published v0.2.2 C3 bundle was installed without a
whole-chip erase. The uploader verified the written flash hash. Startup then
passed with increasing uptime, a ready library, protected All, zero customs,
Blue selected, and the 400 mA computer-USB ceiling. The device reports the new
Dragon Kingdom hostname, an open setup AP and no saved home-network credentials.
Initial LDR readings were approximately 1,400–1,700; touch was initially idle.
These readings establish sensor input, not yet a cover/uncover or touch pass.
The user subsequently confirmed normal dragon lighting, tap to change dragon,
double-tap sleep/wake, hold brightness and visible LDR cover/uncover response.
The first 117 captured sensor samples recorded 13 touch presses, eight selected
dragons, normal/sleep modes, brightness steps 0–10, LDR 152–1,663 (filtered
197–1,653), and automatic gain 10–40. No decreasing uptime was observed. These
are physical C3 results, distinct from the native pin/USB simulations. Wi-Fi
and cold-boot strapping checks remain pending. The earlier S3 Wi-Fi failure
remains open.

C3 raw logs and saved settings are in ignored
`dragon-firmware/.tools/c3-hardware-20261019/`.


The user then disconnected USB for five seconds and reconnected with the touch
pad untouched. Normal visible startup was confirmed; serial independently
passed increasing-uptime/library/400 mA checks after that cold boot.

C3 provisioning to the intended home network succeeded over trusted USB. The
laptop reached authenticated state/library/dragons/alarm endpoints through the
existing cross-network router rule. Headless Edge then exercised the actual
C3 embedded page at 390 × 844, with a desktop screenshot at 1280 × 900. Controls,
sleep/wake, alarm save/reload/restore and preview/stop, Wi-Fi scan, protected All,
empty-profile reload, custom save/copy/delete, favourites and profile-deletion
rehoming passed without captured page errors. These are live-device desktop
browser checks, not physical phone tests. Temporary test data was removed;
only All, zero customs, Blue at 100% glow and the original disabled alarm remain.


Three subsequent ROM-loader hard-reset cycles each rejoined the saved home
network and returned authenticated HTTP state: 7.44, 8.59 and 7.48 seconds after
the loader reset. The serial observations retained the 400 mA USB ceiling.
These three C3 trials passed; they do not resolve or supersede the S3 failures.
Cold startup with the touch pad held (GPIO2 strapping/setup gesture) remains
the next physical check.


The user completed the final C3 cold-start test while holding touch for about
five seconds: normal lighting and phone visibility of `Dragon-Kingdom-7c263d`
were confirmed. The 120-second recorder had completed before this cycle, so it
contains the preceding AP-off runtime, not the held-boot transition. A fresh
post-boot capture at uptime 59–63 seconds independently confirmed AP active,
home Wi-Fi connected, ready All library with zero customs, Blue, normal 100%
glow, automatic light adjustment, disabled alarm, a ready clock and the 400 mA
USB ceiling. The network's last disconnect reason was 202 despite the current
connected state; no transition timing or cause is inferred from that field.
Authenticated HTTP state/library/alarm reads then passed. This closes the
normal/held cold-boot and setup-AP visibility checks on this tested C3 carrier.
It does not establish setup-AP browser access or physical phone browser coverage.

The C3 remains on saved home Wi-Fi with its setup AP open following the held
startup. Test profiles/customs have been removed. No firmware source or binary
was changed during the C3 physical follow-up; both published v0.2.2 board
archives and checksums remain the same. The separate S3 reconnect issue and
external-supply/final-design/endurance gates remain open.


## S3 reconnected after the C3 tests

The user reconnected S3 on COM17. The subsequent
[station-readiness investigation](WIFI-READINESS-2026-10-19.md) identified an
unapplied transmit-power limit, repaired its readiness/return-value handling,
and verified the intended setting physically. Installation and one reset
connected and served HTTP; a later reset and a matrix-off join trial failed.
The current S3 image is v0.2.3, with unchanged storage/partitions and the
400 mA USB ceiling. The earlier S3 reconnect gate remains open. Earlier C3
physical results remain specifically v0.2.2 evidence; the new paired C3 image
is build-tested only.
