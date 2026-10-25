# S3 Wi-Fi bridge acceptance - 25 October 2026 (Sydney)

The user supplied the S3 address and explicitly confirmed normal supply only, laptop USB disconnected before installation. Live preflight identified S3 running beta 2. A fresh user-settings backup was saved in ignored local evidence, and the update route reported no existing transfer.

The S3-specific v1 bridge was signed with the existing matching private key from the checked immutable beta-6 application. Its whole-file SHA-256 is `4b3c83df93e27731155d21f8210e2a308c184e8d0e1e6046e2660eb6224c1054`, built from source `69ba10a5030eaa04855d8bdd82ffa8f43da0d75f`. The signed release-set contract and bridge signature were verified locally. The lamp accepted the signature, acknowledged all 512-byte chunks and verified the completed image before restart. No firmware feed or hosted artifact was modified.

The upload completed in approximately 133 seconds. After restart, the S3 rejoined Wi-Fi and reported beta 6, OTA state 2 (VALID), completed startup validation and a 2400 mA estimated startup ceiling. That figure is firmware-reported, not an electrical measurement. Calibration-present was false; this unit has no chip-bound voltage correction record. It is distinct from the corrected-divider C3, where that flag remains true.

The before/after backup comparison confirmed identical library bytes (profiles, custom creations and associated settings), rotation and room-light settings, plus alarm enabled/time/duration. Only RAM-only phone clock/timezone rules and the enclosing backup checksum were excluded, as in the earlier C3 checks. No restore or reset was performed.

Both Release and Beta metadata checks completed over verified HTTPS with zero reported transport/TLS/socket errors. Both correctly reported that no compatible new-format online release is published yet. No online installation was offered or attempted.

The live browser displayed beta 6 / ESP32-S3, existing custom creations, completed home-Wi-Fi wording, the S3-specific package name and the revised Parent settings. Parent unlock and relock were checked. Normal page opening resynchronized the phone clock. Private backups, device hostname and diagnostic snapshots remain in ignored local output.

This records one successful physical S3 bridge OTA, validated startup, settings comparison and webpage/update-metadata check. Detailed touch gestures, LDR, phone setup, router outages, interrupted restore, rollback, complete online firmware installation, USB recovery and overnight operation remain pending. Basic lighting/touch received the user confirmation recorded below. It is not finished-product acceptance.

## User observation

After being asked to check normal S3 lighting and touch response, the user reported "s3 works good." Record this as user-reported normal lighting and basic touch operation. No individual gesture, LDR response, electrical measurement, phone setup, router outage, rollback or overnight result is inferred.

## Room-light sensor observation

The user covered and uncovered the room-light sensor on both lamps after being asked to check smooth dimming and brightening, and reported "tested both- working." Record user-reported LDR/automatic dimming pass on beta 6. This does not establish electrical, thermal, router-outage, rollback or overnight results.

## Normal-supply power-cycle observation

After being asked to power-cycle each lamp using its normal supply with laptop USB disconnected, wait approximately one minute, and check lighting/touch and webpage reconnection, the user reported "both work." Record these as user-reported successful power-cycle, basic lighting/touch and home-network webpage reconnection on both beta-6 lamps. No measured startup timing, setup-AP phone experience, prolonged router outage, rollback, thermal or overnight result is inferred. This is separate from the USB-specific production startup check.
