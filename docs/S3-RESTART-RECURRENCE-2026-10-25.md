# S3 restart recurrence - 25 October 2026

The user reported that the S3 was repeatedly restarting again and asked for tests while away. This supersedes the earlier brief no-restart report; the cause was never established or fixed. The currently published beta-9 application bytes were retained throughout this investigation. No firmware, flash, calibration, thresholds or saved user settings were written. The separate corner-test bench board was not connected; the identified main S3 was COM21 when enumerated.

## Physical/live observations

The initial S3 endpoint and USB port were unavailable, while the beta-9 C3 remained reachable. A five-minute S3 observation recorded 66 samples, 20 reachable state samples and 5 captured uptime drops. All retrieved support samples reported resetReason=1, VALID beta 9 and a 400 mA ceiling with computerUsb=true. The earlier current-power question was not answered; the last explicit user power confirmation was laptop USB connected with external power off. No agent changed the physical power arrangement. Actual dual-power absence cannot be verified from the USB flag alone.

The C3 network control succeeded in all ten checks. S3 free heap in retrieved support samples was approximately 232–237 kB; the short boot windows do not establish a long-term memory trend. Five temporary RAM-only brightness-zero commands were acknowledged. Some subsequent state samples retained Glow 0 before uptime dropped and saved starting Glow 100 returned on reboot. No power ceilings were raised, no deliberate bright-load sweep was requested, and the colour or calibration was not modified.

A separate 150-second serial watch captured 118 uptime reports, 6 drops and 43 port open/loss events. Successful startup reports retained the 400 mA computer cap and no current startup failure. No panic/watchdog report was captured; native USB disconnection can prevent boot/crash output capture, so this does not prove there was none. The running ESP image digest matched the accepted beta-9 application.

## ROM isolation

After both observers closed their handles, a ROM-only chip-identity command identified the expected ESP32-S3 and explicitly left it in the bootloader using --no-stub and --after no-reset. It performed no flash write. The next no-reset probe, ten seconds later, failed because COM21 no longer existed. A later bounded attempt to start a read-only flash capture found no matching USB device within 25 seconds, so no read was started and no full-flash capture was produced.

The same device later reappeared on COM21 and over HTTP running the normal beta-9 application. Its uptime was about 57 seconds, resetReason=1, startup VALID, and the USB ceiling remained 400 mA. No hard-reset/normal-boot command had been issued between the successful ROM entry and this application observation. This is evidence of instability outside the Dragon application: a USB/power/board reset path or host-induced hardware reset remains possible. It does not isolate the cable, USB port, connector, regulator, reset circuit or other board hardware.

Windows subsequently reported the target USB serial/composite/JTAG devices OK with problem code 0 during a reachable window; that snapshot does not clear intermittent faults. The final acknowledged temporary lights-off command changes only RAM, and any later reboot may restore the saved starting Glow. The final 90-second observation is recorded below when complete.

## Software checks and limits

Reviewed the actual startup and boot-validation paths. A VALID degraded boot does not request rollback, and normal OTA restart is scheduled only after a complete verified image. A startup power failure can also repeat a dim bottom-row red diagnostic without rebooting; the current live uptime drops distinguish today's captured events from that indicator. Historical invalid-divider records remain undated and are not assigned as the cause of this recurrence.

Recompiled and passed the existing native startup, lifecycle and RGB current-budget suites. They exercise real application logic with hardware fakes, not the ESP radio, USB driver, regulator or bootloader. They do not establish board stability. The ROM result means the colour renderer is not necessary for the observed USB instability; no speculative firmware fix was made.

## Publication and next isolation step

Added a prominent S3 reliability follow-up to the existing beta-9 release notes, preserving every release asset and channel pointer. It records that the earlier short stability report is not a fix or production/endurance acceptance.

The next physical isolation step, when someone is home, is a known-good data cable and a different direct laptop USB port with external/main power disconnected. A later separate product-supply/cable test requires physically unplugging laptop USB first. Continued failure in ROM with a proven cable/port would direct attention to the board power/reset path. No meter measurement or exact failed-component diagnosis is claimed. All raw serial/USB/ROM/support evidence remains in ignored private output directories.

## Final state

The last approximately 90-second lights-off observation returned 17 support samples with increasing uptime from 101734 to 187436 ms, no captured reset and Glow 0 throughout. This is a short quiet interval after many earlier failures, not a demonstrated repair or proof that LED load is the sole cause. The S3 was left running the same beta-9 application with temporary lights off; parent sessions and serial handles were closed. Its saved starting Glow remains unchanged and can return after a reset. The C3 was not modified. A fresh local service ledger entry marks the S3 startup/reliability check failed, with other acceptance categories pending.

## Subsequent power confirmation and older-firmware comparison

The user corrected their asynchronous answer and explicitly confirmed laptop supply only, with external power off. This confirms the physical arrangement for the detected-USB tests above. They then requested an older-firmware comparison; see [baseline, service and results](S3-FIRMWARE-COMPARISON-2026-10-25.md). The earlier temporary no-reset interval remains insufficient to claim a repair.
