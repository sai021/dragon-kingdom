# Physical acceptance - fixed S3 and C3 products

Run separately for each board and record unit identity privately in
`dragon-firmware/.tools/shipping/ledger.jsonl`. All items below remain pending for
this local candidate. Software simulations do not establish physical acceptance.

Before each operation confirm current ROM/device identity and power arrangement.
Never connect laptop USB and external/main power together. Use internal USB for
service. Unplug it before testing the assembled lamp on its external supply.

- Cold boot on specified supply/cable, ordinary VALID boot and repeated power cuts;
  verify startup estimate, visible LEDs and no unexpected restart.
- Tap, double tap, brightness hold, LDR response, low-power touch-only fallback;
  confirm 400 mA ceiling under computer USB separately from external-supply tests.
- Actual iPhone and Android: startup setup AP, no-internet prompt, QR/manual fallback,
  login-free play, parent unlock/relock, home join and 15-second handover. Bookmark
  `.local` in the normal browser. Check a DHCP address change.
- Router outage, repeated drops and prolonged absence: bounded retry, no AP reopen,
  responsive touch/animation, correct mDNS restoration. Exercise scans, queued HTTP
  responses and online/offline updates around the disconnect.
- Save/reboot profiles, creations, alarm and rotation; preserve protected All and
  voltage calibration. Distinguish temporary glow from saved starting glow.
- Complete online and offline OTA on both boards; duplicate/lost chunk acknowledgements,
  cancel/retry, interrupted uploads, wrong board, old/equal tags, missing capability,
  schema mismatch, damaged signature, calibrated C3 versus ordinary C3.
- Trial boot with healthy and failed storage/power, populated and empty alternate
  slots; VALID ordinary degraded boot must not roll back. Check initial USB migration
  with erased OTA metadata and failure of confirmation/rollback APIs.
- Restore interruption at each namespace write and journal deletion; retry a valid
  transaction. For corruption, save/read-verify private raw NVS before deliberate
  service abandonment. Inspect every user setting afterwards for a mixed snapshot.
- Reopen phone page to resynchronize an offline clock after power loss, check alarm
  readiness and scheduled sunrise. Run overnight with periodic uptime/heap checks,
  touch checks and external-supply thermal/current observations.

`STARTUP PASS` is only firmware/tag/board/storage/USB-ceiling/VALID evidence. Record
LED, touch, LDR, external-power, phone, reconnect and overnight results separately:

    python tools/shipping_ledger.py --bundle IMMUTABLE_RELEASE --unit LOCAL_ID --board c3 --calibrated yes --startup pass --led pass --touch pass --ldr pass

Omitted results stay pending. Do not put SSIDs, credentials or child names in the
unit identifier. External-power acceptance must be recorded only after its separate
test with laptop USB disconnected.
