# Low-light colour - 25 October 2026

The user observed colours becoming redder as brightness falls. Source inspection found a reproducible software bias: truncating RGB components and selecting just one dominant channel when all three rounded to zero. Ties selected red, so neutral RGB(20,20,20) at tiny positive gain became RGB(1,0,0). Separate ambient and manual Glow rounding compounded quantisation. This establishes a software cause, not a measurement of the assembled LEDs' spectral response.

## Beta 9 implementation

Source `fc1b770` combines ambient and manual Glow into one final gain and rounds to nearest. The visibility floor is symmetric: each nonzero channel at least half the input peak receives at least one count. Neutral whites keep RGB, yellow keeps RG, and primaries do not gain other channels. At tiny gains, RGB(200,190,180) may become equal channels: exact ratios cannot always be represented with one or a few 8-bit counts. This trades some saturation resolution for a balanced floor instead of arbitrary red selection.

The current limiter uses the same monotonic scaling. Its budget always wins if the multichannel minimum cannot fit. No channel can exceed the already limited input during dimming. The 204/255 maximum channel cap, computer-USB 400 mA ceiling, startup policy, calibration, saved schemas, network locking, protected All and artwork are retained. There is no temporal dithering or assumed physical white-balance calibration. Sunrise still bypasses ambient/manual Glow but benefits from the shared rounding correction; raw bench diagnostics keep their separate scaling.

The ten room-light bins retain beta 8 gains and sensor logic. For an otherwise full 204 channel at Glow 100%, their outputs are now 3, 5, 10, 18, 31, 51, 82, 122, 163, 204. These are digital drive values, not measured optical percentages.

## Software verification

59 Python tests, all 18 native suites and the simulated phone-browser workflow pass. New checks cover neutral/near-neutral colour floors, pure primaries, black and zero gain, RGB permutation symmetry, monotonic output, current budgets including an unaffordable RGB floor, and neutral output across combined ambient/manual levels. Existing presets, gesture, sensor, calibration, startup, sunrise, USB and parent/update regression suites pass. No simulated result is treated as physical colour evidence.

## Physical colour acceptance

A dark-room comparison of the assembled lamps remains pending. Any remaining warm tint may come from LED channel balance, diffuser/artwork or human perception and should be assessed after this software correction. The separate USB-only four-corner S3 bench is retained unchanged as a reference.

## Builds and local release

Both pinned builds passed from `fc1b770c609553909766fed0452c9b2e28cc3d1e`. Existing OTA partition slots were validated by the release preparer. The signed two-board beta-9 set uses the existing trust root and remains local; nothing was published.

| Board | Application bytes | Whole-file SHA-256 |
| --- | ---: | --- |
| S3 | 1,399,744 | `370caaaad4dfb574142fa1683765e729c5b917b6608a06ae03cc91f0e6e9dd42` |
| C3 | 1,443,920 | `30beaf970ec189641e63bb52d8de10db69e2bd9e523f78cab3231151935e2501` |

## Wi-Fi installation evidence

Both lamps were re-identified on beta 8 with computerUsb=false before backup/upload. The C3 accepted its signed beta-9 image, restarted and reached VALID, retaining its divider calibration and persistent settings. The first S3 transfer lost HTTP/Wi-Fi reachability near 71% before finalisation; it was not treated as successful. The S3 later reappeared on beta 8 at the same address, confirming that the incomplete update had not replaced the running image. A fresh signed upload was then started. This disconnect remains reliability evidence rather than being hidden by a later retry.

The second S3 upload also lost reachability, this time near offset 30,720, without finalisation. On return it still reported beta 8, VALID, no active update, uptime about 22 seconds and resetReason=1 (power-on). This is evidence of a recent restart, not proof of its physical cause. Further uploads were held while asking whether the user had switched power. The C3 finished its online metadata check with all HTTPS diagnostics zero, automatic light active, room-light step 10 and Glow 100%. Parent sessions were logged out. S3 beta-9 installation and user optical acceptance remain pending.

## Unexpected S3 restart follow-up

The user explicitly confirmed that the S3 restarted by itself, without them switching power. No further upload was attempted. Its last retrieved resetReason=1 corresponds to ESP_RST_POWERON in the pinned IDF 5.4 header, distinct from ESP_RST_SW, ESP_RST_PANIC, watchdog and ESP_RST_BROWNOUT. This points toward a power/reset-path event but does not prove a supply, cable or board fault. Source review confirms that normal firmware OTA restart is scheduled only after complete hash/image validation and boot-slot selection; neither interrupted transfer reached that stage. The earlier successful startup load test is not proof of runtime power stability.

A short idle observation then found the S3 HTTP endpoint unreachable while the C3 remained reachable. The user was asked whether the S3 remained lit/responded to touch, repeatedly showed startup, or was off. Wi-Fi reachability alone cannot distinguish a restart, wireless loss or an unresponsive application. Further S3 update and optical acceptance remain pending diagnosis; no USB or power arrangement was changed.

The user then confirmed repeated restarting/startup flashes while idle. This establishes a user-observed restart loop, not just HTTP loss. Further firmware attempts remain stopped. The next physical isolation step is to disconnect the S3 product supply and try a known-working regulated 5 V adapter/cable, retaining product-supply-only power with no laptop USB. The software colour fix cannot yet be accepted on the S3, which last reported beta 8; the C3 remains the beta-9 comparison unit. The reset loop's cause remains unproven.

## USB service on the same S3

The user connected the lamp's S3 to laptop USB and explicitly confirmed external power off. The connected COM21 USB serial identity differs from the earlier separate COM17 bench S3. The initial serial handle dropped once; enabling CDC output with DTR=true/RTS=false then produced beta-8/schema-1/VALID status. Uptime increased through about 62 seconds with session_max=400mA and computer_usb_cap=1. Startup at the two USB-limited load levels reported divider-derived values about 5.08–5.13 V, with no current startup failure; these are onboard estimates, not meter measurements or an external-supply test.

The retained historical failure ring contains four invalid-divider startup entries (about 1.62, 2.85, 1.62 and 2.19 V at the rejected sample). These have no timestamps and do not prove the cause of today's restart loop; no correction or diagnostic record was changed. USB stability at a lower load does not isolate a cable, external supply or internal board fault.

The existing signed beta-9 recovery set was selected after confirming runtime compatibility. The service tool re-identified ESP32-S3 in ROM, validated the on-device NVS layout and began a private raw NVS backup before any flash write. No erase-flash or NVS write is used. Final installation and preservation evidence follow after the service completes.

USB service completed successfully. All 20,480 NVS bytes match before/after. The S3 reports beta 9 in app0, startup ready=1 and ota_state=2; the service checker also verified the running image digest against the signed prepared release. A further 35-second serial observation gave 30 increasing uptime reports from 35345 to 70342 ms, retaining the 400 mA USB ceiling and VALID status without a captured reset. This is a short USB stability check, not proof of external-power recovery. Both main lamps now have the beta-9 colour correction. Actual dark-room colour acceptance and the S3 external-supply restart diagnosis remain open. Serial handles were closed, and the S3 was left USB-only; no external supply was connected.

## User observation and publication

The user explicitly praised the colour accuracy after the correction, then reported that it was working with no restarts. The latest power arrangement was not separately confirmed, so extended external-power acceptance remains pending. At the user's request beta 9 was published as an opt-in manual-download prerelease, with all five CI jobs passing and application bytes identical to the tested ones. See [publication, artifacts and provenance](BETA-9-PUBLICATION-2026-10-25.md). Earlier statements that nothing was published describe the preceding local-test stages.
