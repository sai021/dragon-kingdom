# S3 physical test record — 19 October 2026

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

## Remaining physical limits

C3 carrier orientation/strapping/sensors, deployed external supply/current/thermal
behaviour, final prints and Gerbers, optical separation/colour agreement,
physical phone platforms, deliberate router loss, cold power-cut/NTP recovery
and longer endurance remain separate checks. The old mechanical/PCB assets
remain prototypes. No simultaneous USB/external-power test was performed.

Raw captures, pre-update NVS, endpoints, logs and screenshots are kept under
ignored `dragon-firmware/.tools/kingdom-release-20261019/`. Do not publish them.
