# Software checkpoint — 18 October 2026

Historical checkpoint. Current repaired software is recorded in the
[19 October repair report](RELIABILITY-FIXES-2026-10-19.md). The current
[manual](USER-MANUAL.md) is edition 0.5, eight pages, 19 October 2026;
edition 0.4 references below describe the earlier checked edition.

Status: verified development-prototype software checkpoint before the subsequent
whole-wing/glitter change. See PROJECT-STATUS.md and TESTING-HANDOVER.md for
the newer builds; hashes and bundle selections below are historical. This does not
approve family distribution or final hardware manufacture. Start live testing
from [Testing handover](TESTING-HANDOVER.md); the dated
[hardware record](HARDWARE-TEST-2026-10-18.md) retains physical evidence.

## Firmware and saved images

Fresh builds from the current editable sources passed for both targets.
All three upload binaries for each target are byte-for-byte identical to its
previous saved network-switch bundle; no replacement image or device upload
was needed. The batch flasher's existing selections remain valid.

| Target | Compiler app usage | Upload app file | Static RAM | Saved bundle directory |
| --- | ---: | ---: | ---: | --- |
| ESP32-S3 | 1,147,250 bytes | 1,147,392 bytes | 51,300 bytes | `20261018-175703-network-switch-s3` |
| ESP32-C3 | 1,171,166 bytes | 1,171,312 bytes | 42,256 bytes | `20261018-175703-network-switch-c3` |

The upload-file sizes include image overhead and are checked against the
actual **1,572,864-byte** custom app partition. The compiler's generic 16 MB
percentage is not the configured flash capacity or the partition limit.
S3 remains 4 MB flash / 2 MB PSRAM; C3 remains 4 MB flash / DIO / no PSRAM.

Application SHA-256:

```text
S3 fd29ba781552609bed390ba254a72cb519d8d7672e6dce310eff7a1b41f634b3
C3 9df20c0d20af2151d79e3ac30ac162df44dc67f21dbaa8d651f6cd62b5b6fad3
```

`flash_support.load_bundle()` revalidated app, bootloader and partition hashes
and target configuration for both selections. Local manifests and binaries
remain under ignored `dragon-firmware/.tools/batch-flash/`. The ignored
`dragon-firmware/.tools/release-20261018/checkpoint.json` records checksums for
63 firmware, web, catalog, tool and test source files, plus both bundle hashes.
Build logs are beside it. No credentials or raw captures belong in this document.

Network-event locking, All protection, migration, separate alarm storage,
8.5 dBm Wi-Fi TX policy and the 400 mA estimated computer-USB ceiling remain
unchanged. Generated headers were refreshed by the normal build from editable
web/catalog sources. No firmware behaviour was changed during consolidation.

## Verification

| Check | Result | Boundary |
| --- | --- | --- |
| Python regressions | 23 passed | Includes flasher/Tk, catalog and provisioning helpers |
| Native C++ | All 13 suites passed | Fakes; no radio or physical C3 validation |
| Simulated phone browser | Passed | 390 × 844; mocked HTTP, not a physical phone |
| Both Arduino builds | Passed | No upload in this consolidation |
| Saved upload bundles | All hashes passed; identical to fresh outputs | S3/C3 kept separate |
| User manual | Edition 0.4, seven pages regenerated and visually inspected | Prototype instructions |
| Resumed live embedded UI | Controls, alarm save/reload and preview/stop, Wi-Fi scan, profile/custom/favourite saves passed | Desktop browser; details and limitations in handover |

The user identified local-device isolation on the original Wi-Fi network.
Moving the laptop to an allowed network restored HTTP. An ESP32 connection
alone does not establish that a phone/computer can reach it; isolated networks
can block both mDNS and numeric HTTP. Documentation now explains this recovery.

The UI serializes requests and ignores new play/save commands while a command
is pending. A rapid sleep click after a glow change was ignored; a subsequent
click worked. The parent guide and manual now advise waiting for each result.
Queueing, disabling controls or clearer busy feedback remain future improvements.
The live browser tool stalled on a delete confirmation; that is not evidence
of a firmware delete failure. Cleanup used authenticated API calls limited to
new test objects. UI deletion/copy/rehoming remain open live-browser checks.

Final verified device state after live tests: All, Blue, 100% manual glow,
no custom creations or temporary profiles; daily alarm disabled at 07:00 with
a 20-minute duration, no preview active. Ambient and power limits still apply.

## Documentation set

- [README](../README.md): current project entry point and evidence boundaries.
- [Project status](PROJECT-STATUS.md): consolidated history and remaining gates.
- [Testing handover](TESTING-HANDOVER.md): live device state and next checks.
- [Developer guide](DEVELOPMENT.md) and [batch flashing](BATCH-FLASHING.md): reproducible builds, checks and programming.
- [Parent guide](PARENT-GUIDE.md): prepared-prototype quick start.
- [Manual source](USER-MANUAL.md) and [printable manual](../output/pdf/dragon-kingdom-user-manual.pdf): edition 0.4.

## Remaining release gates

Physical iPhone Safari and Pixel Chrome, browser Wi-Fi join/wrong-password/
recovery, live UI copy/delete/ownership/rehoming and rapid-control recovery
need completion. Longer uptime, router loss/recovery, whole-house coverage
and clock/NTP recovery after complete power loss remain open.

C3 has software-only evidence. Confirm fit/orientation, GPIO2 boot strapping,
ADC against a meter, touch, matrix, Wi-Fi, storage and USB limiting physically.
Validate deployed supply/current, sustained brightness and cable separately;
disconnect laptop USB before external-only tests. Never power both inputs.

New STL files, build photos and Gerbers are awaited. Existing mechanical/PCB
assets are earlier prototypes; optical zone reconciliation, native DRC and
assembly checks are not signed off. Parent protection and final recovery flow
are still release work. Supplied artwork and CAD notices retain their provenance.
