# S3 firmware comparison - 25 October 2026

The user asked to try the previous firmware to test whether the new software caused the restart loop. Their corrected power confirmation is laptop USB only, external/product power off. The S3 is the same COM21 lamp identity; the separate bench S3 is not attached. The C3 is not changed.

## Baseline and controls

The earlier restart record includes actual beta-8 failures before the beta-9 colour fix was installed, so the new colour calculation is not required for those historical events. Earlier beta-9 testing captured repeated power-on resets at the 400 mA USB ceiling and loss of the USB port during ROM-only testing. These remain relevant but do not replace the requested firmware comparison.

A fresh beta-9 baseline restored temporary Glow to 100% without changing its saved profile, power cap or calibration. Over approximately 122 seconds, all 37 support requests succeeded, uptime increased from 712,066 to 830,901 ms, and no reset was captured. Automatic room-light control was active; sampled gain was 250 permille, step 6. This demonstrates a quiet interval, not an earlier repair. The fault is intermittent, so a similarly short pass on an older image cannot establish causation.

Verified the immutable signed beta-8 and beta-7 two-board release sets. Both retain calibration capability 1 and saved schema 1; their S3 bootloader/partition hashes match beta 9 exactly. The source test does not change pins, calibration, startup thresholds or the 400 mA computer-USB ceiling.

| Candidate | Source | S3 application SHA-256 |
| --- | --- | --- |
| beta 9 | fc1b770 (same app at d207609) | `370caaaad4dfb574142fa1683765e729c5b917b6608a06ae03cc91f0e6e9dd42` |
| beta 8 | f524ddf | `90c59817e0d246348748536a7c35f7682a3312cd1b244bd28255a080e3ae4b81` |
| beta 7, if beta 8 also fails | 89489b6 | `ab7a5ce3ead93bfc376b900ff41981379a4c4e663b3d45870a7d8799b35ac7ce` |

## Service and comparison

A fresh private user-settings backup was captured after the baseline. The existing signed USB recovery tool re-identifies the ESP32-S3, checks compatibility, saves raw NVS before writes, and verifies exact NVS preservation before reset. Explicit service downgrade is authorized by the user's request; ordinary signed web updates retain their newer-version enforcement. No unsigned or relabelled package is used.

The plan is to install beta 8 and observe it at temporary Glow 100% under the same USB arrangement. Beta 7 is a conditional further check if beta 8 also restarts; it predates the night-brightness changes. Ambient light is measured rather than artificially overridden, so any gain differences are recorded as a comparison limitation. The service resets OTA metadata, which also prevents attributing any later stability solely to application version.

Detailed private backup, serial, ROM and HTTP evidence stays in ignored output. Results follow after completion.


Beta-8 installation completed with expected running-image/VALID checks and byte-for-byte preservation of all 20,480 NVS bytes. Ambient gain was 400 permille/step 7 after service, differing from the 250-permille initial beta-9 baseline. To control that variable, beta 8 was switched to RAM-only automatic-light off/full gain with Glow 100% and the USB ceiling still 400 mA. The repeat beta-9 phase will use the same full-gain conditions if beta 8 remains stable. Saved light thresholds, profiles, voltage calibration and USB ceiling are not changed by the temporary override.


Beta 8 completed approximately 301 seconds: 90 samples, 89 support replies, zero captured uptime drops, and one failed request without an observed restart. Uptime increased from 11,893 to 309,119 ms. The last reset classification was 11, consistent with the deliberate USB service reset, rather than the spontaneous power-on resets seen earlier. Its full-gain/automatic-light-off portion contained 60 successful support samples spanning about 202.2 seconds. No beta-7 escalation was needed because beta 8 did not reproduce the fault.

Beta 9 was then restored for an A/B/A return test using the same signed published application. The service again verified expected image/startup VALID, the 400 mA USB ceiling and exact preservation of all 20,480 NVS bytes. The return observation uses Glow 100%, automatic light temporarily off and full gain for five minutes; automatic control will be restored afterward. This tests whether the fault reappears upon returning to the new version, without claiming that a short stable old-version interval proves causation.


## Completed A/B/A result

| Phase | Observation | Support replies | Captured uptime drops |
| --- | ---: | ---: | ---: |
| beta 9 initial, automatic light active | about 122 s | 37/37 | 0 |
| beta 8, automatic then full gain | about 301 s (about 202 s full gain) | 89/90 | 0 |
| beta 9 return, full gain throughout | about 303 s | 90/91 | 0 |

The return beta-9 run kept automaticLight=false, gain 1000, selected Glow 100% and estimated USB ceiling 400 mA throughout every successful support sample. Uptime rose from 42,177 to 342,046 ms. Each five-minute run had one failed support sample, but subsequent uptime continued without a captured reset. The tests therefore did not reproduce a fault unique to beta 9. They do not establish that either firmware fixes the intermittent problem, nor clear the previously captured resets/ROM USB disappearance. Beta 7 was not installed because beta 8 did not reproduce the failure.

After the comparison, restored automatic light control and temporary Glow 0, matching the pre-test lights-off state. Final beta 9 reports VALID, ordinary S3 calibration absent and a 400 mA detected-computer ceiling. A fresh logical backup preserved all compared persistent library/profile/alarm/rotation sections; the same known volatile clock/timezone/checksum exclusions used in earlier service comparisons were retained. Both USB services independently preserved all 20,480 raw NVS bytes before reset. No supplied data, saved thresholds, calibration, pins, release assets or C3 firmware changed. Serial handles were closed and parent sessions logged out.

The S3 is left on the published beta-9 application with automatic dimming enabled and LEDs temporarily off. The rollback did not produce a demonstrated fix and the return test did not reproduce the fault. A known-good USB cable/direct port test, followed by a separately powered product-supply test, remains the next physical isolation work. The release's unresolved-S3 warning remains appropriate and was not removed.
