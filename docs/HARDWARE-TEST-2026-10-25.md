# Corrected C3: Wi-Fi bridge acceptance, 25 October 2026 (Sydney)

User identified the accessible C3 as the unit with the aberrant divider and confirmed laptop USB was disconnected. The previous record documents its chip-bound 1.790 divider correction. No USB access or new calibration write was performed.

The original ignored signing key was located in the established release-signing directory. Its public key matches the current and beta-3 trust roots. Maintained preparation tooling verified source/build provenance at `6b69972` and produced a signed immutable two-board beta-4 set locally. A separately named v1 C3 bridge was signed from that same checked calibration-aware application. No release feed or hosted artifact was changed.

Live preflight confirmed C3, beta 3, the same device hostname as the earlier private snapshot, and no existing upload. A fresh settings backup was saved privately. The C3 accepted the bridge signature, acknowledged every 512-byte chunk, verified the completed image and restarted. Upload took approximately 160 seconds with no retries. Image SHA-256: `f90288f48628b0d5f22fd772fb019b79a7c6d6b3b8db7e9839341538b694d450`.

After restart, live support reported beta 4, C3, OTA state 2 (VALID), validated=true, startup confirmed, all levels passed, calibrationPresent=true and estimatedCeilingMa=2400. At 31.7 seconds uptime, free heap was 156,000 bytes, minimum heap 140,768 and largest block 114,676. These are device-reported estimates/diagnostics, not electrical measurements. Wi-Fi rejoined successfully.

The initial exact-backup comparison failed. Investigation using the native snapshot layout established that only RAM-only clock/timezone rules and the enclosing checksum differed. Before restart, the disabled alarm held phone-synced timezone rules; after restart these returned to zero. The clock-sync handler intentionally does not persist them unless the alarm is saved. Library bytes, rotation, light settings, and alarm enabled/time/duration were unchanged. Reopening the webpage resynchronizes the clock. No settings restore was performed.

Private backups, hostname, transfer record and support snapshots remain in ignored `.tools/device-checks/`. The support endpoint confirms calibration presence, not the exact 1.790 value; raw calibration/NVS equality was not checked over Wi-Fi.

This is one successful physical legacy-bridge OTA and validated startup on the corrected C3. It does not establish ordinary-C3 or S3 acceptance, physical LED/touch/LDR behavior, measured current/thermal safety, phone-browser compatibility, router-outage recovery, v2 OTA, rollback, interrupted restore, USB recovery or overnight stability. Those remain pending. Parent session was locked after inspection.

## User observation after beta 6

After being asked whether the corrected C3 lights normally and responds to touch, the user reported "c3 good." Record user-reported normal lighting and basic touch operation on beta 6. Detailed gestures, LDR response, electrical measurements, phone setup, router outages, rollback and overnight operation are not inferred. See the beta-6 implementation and evidence in [the parent-page follow-up](PARENT-PAGE-FIXES-2026-10-25.md).

## Room-light sensor observation

The user covered and uncovered the room-light sensor on both lamps after being asked to check smooth dimming and brightening, and reported "tested both- working." Record user-reported LDR/automatic dimming pass on beta 6. This does not establish electrical, thermal, router-outage, rollback or overnight results.

## Normal-supply power-cycle observation

After being asked to power-cycle each lamp using its normal supply with laptop USB disconnected, wait approximately one minute, and check lighting/touch and webpage reconnection, the user reported "both work." Record these as user-reported successful power-cycle, basic lighting/touch and home-network webpage reconnection on both beta-6 lamps. No measured startup timing, setup-AP phone experience, prolonged router outage, rollback, thermal or overnight result is inferred. This is separate from the USB-specific production startup check.
