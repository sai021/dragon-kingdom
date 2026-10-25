# Lower night glow - 25 October 2026

The user reported that the previous lowest automatic brightness was too bright overnight. A separate USB-only S3 bench test used the four corners (red, green, blue, white), retaining the 400 mA ceiling. The user could see the lowest nonzero output (1/255 per active colour channel), then sampled approximately 1% full-scale drive (3/255, 1.18%). Those are digital channel values, not photometric measurements. Private ROM/serial evidence is in ignored local output. The bench firmware was not flashed; no saved calibration/settings were changed by those commands.

## Beta 8 behavior

Source `f524ddf` retains the existing 204/255 maximum channel drive (80%), all current limits, power-before-dimming order, protected All/catalog IDs, network locking and saved-data schemas. The ten ambient ADC bins still use the same filtering, hysteresis and dwell. Their gains are now 15, 25, 50, 90, 150, 250, 400, 600, 800, 1000 permille of the already power-limited frame. Fading settles exactly at its target by up to 10 permille each 30 ms; ADC remains 4 Hz.

At selected Glow 100%, a channel that could otherwise reach 204 now follows:

| Room-light level | Channel drive | Full-scale drive |
| ---: | ---: | ---: |
| 1 - darkest | 3/255 | 1.18% |
| 2 | 5/255 | 1.96% |
| 3 | 10/255 | 3.92% |
| 4 | 18/255 | 7.06% |
| 5 | 30/255 | 11.76% |
| 6 | 51/255 | 20% |
| 7 | 81/255 | 31.76% |
| 8 | 122/255 | 47.84% |
| 9 | 163/255 | 63.92% |
| 10 - brightest | 204/255 | 80% |

Glow remains the saved relative 0/10..100 limit, preserving existing profile meanings. Artwork colours, session current limiting and selected Glow can reduce output below the table. The existing one-count floor preserves already-lit pixels at very low gains, so this is not an absolute 1% floor on every pixel. Black pixels and Sleep stay black. Sunrise retains its own ramp. The old nominal darkest reference was 20/255 (about 8% full scale); the new 3/255 reference is substantially lower. User perception and overnight comfort still need confirmation on the assembled lamps.

The parent support export now includes automaticLight, ambientGainPermille, roomLightStep and glowPercent; serial sensor output explicitly labels light_gain_permille. No calibration or profile migration is needed. The webpage explains the low-night/80%-cap range and the meaning of Glow.

## Software checks and builds

59 Python tests and the phone browser workflow pass. All 18 native suites passed after correcting a compile error in the newly added test. Tests check the exact 204-to-3 corner reference, monotonic gain table, stable sensor bins and fade endpoint, unchanged gestures/calibration, visibility at all session ceilings, explicit Sleep/black, and preserved current limits. Fresh pinned both-board builds passed.

| Board | Application bytes | Whole-file SHA-256 |
| --- | ---: | --- |
| S3 | 1,399,696 | `90c59817e0d246348748536a7c35f7682a3312cd1b244bd28255a080e3ae4b81` |
| C3 | 1,443,920 | `3d35905559da6165519f1c642d2caa1d3c1eb12745112a968e28a3222f7c0918` |

Both fit the existing OTA slots. The signed beta-8 set was prepared locally with the existing matching key and source/build provenance. Installation evidence is recorded below when live verification completes. No release or hosted asset has been published.


## Live installation

Both known lamps were re-identified on beta 7 with computerUsb=false and the established product-supply arrangement. Fresh private backups were taken before separate signed Wi-Fi uploads. The S3 upload completed in about 120 seconds and the C3 in about 153 seconds. Both returned on beta 8, reached VALID startup, preserved persistent settings and retained their respective calibration states (corrected C3 present; ordinary S3 absent). Online metadata checks completed with all HTTPS error codes zero. Parent sessions were locked after verification.

Live support confirmed automaticLight=true and Glow 100% on both. At the moment sampled, S3 was at room-light step 5 / 150 permille and C3 at step 10 / 1000 permille, consistent with their different current sensor readings. This is not a dark-room optical measurement. User verification of the new assembled-lamp darkest level and overnight comfort remains pending. The separate USB S3 bench remained at its approximately 1% corner reference and was not updated.
