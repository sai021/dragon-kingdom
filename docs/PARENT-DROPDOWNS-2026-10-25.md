# Parent dropdowns, power information and backplate procedure - 25 October 2026

User reports Wi-Fi controls and network search working during the two-lamp test session. Phone operating systems were not specified; this does not establish captive-portal/iPhone/Android setup coverage.

Implemented at `89489b63e84bce2bb23b74ec07b6381d167c2924`, candidate beta 7:

- Connection & power is collapsed by default, contains home addresses, and shows the existing computer-USB detection flag plus estimated startup ceiling. Product-supply mode explicitly means no computer USB was detected; neither source wattage nor measured current is inferred. Existing 400 mA computer-host protection is unchanged.
- Parent subsections are individually collapsed: Home Wi-Fi, Open setup Wi-Fi again, Support details, Backup & restore, Firmware update, Reset saved data, USB recovery & backplate. Polling preserves the chosen open state; relocking closes the protected subsections.
- Support details explains the purpose and contents of the local troubleshooting download and explicitly excludes passwords, tokens, Wi-Fi names and custom dragon names.
- The user's exact backplate procedure is reflected in the webpage, USB recovery guide, parent guide, USB tool instructions and manual edition 0.9: disconnect product power; remove the top rear screw; push the release tab through the keyhole with a screwdriver; open the backplate; connect laptop USB-C to the ESP32 on its centre main board. After recovery disconnect laptop USB, seat the bottom USB-C and LDR in their slots, press the top closed, replace the screw, then restore normal power.

## Verification

The updated phone browser workflow passes. It checks initially closed sections, explicit opening, closing on lock, retained connection-panel state during polling, 22-pixel checkboxes, both power modes, support download/explanation and recovery text. All 18 native suites passed. An initial concurrent Python run aborted during Tkinter teardown; a clean serial rerun passed all 59 tests. No physical USB tool operation was performed.

Fresh pinned S3 and C3 builds passed. Signed immutable beta-7 packages were prepared locally with the existing key. Both lamps were updated over Wi-Fi on their previously confirmed normal-supply-only arrangement, without laptop USB. The S3 upload took approximately 121 seconds, C3 145 seconds. Both reported VALID startup and identical persistent user settings (excluding transient clock rules). The C3 retained calibration-present=true; the S3 remained false.

Both live webpages report beta 7, product supply/no computer USB detected, and a 2,400 mA estimated startup limit. Both showed the default collapsed connection panel and seven collapsed parent subsections. The support explanation and full backplate procedure were opened and checked on the S3. Both parent sessions were left locked. Online metadata checks still reach GitHub successfully and reject the older published feed with the clear compatibility message.

The manual now has nine pages. All nine were rendered and visually inspected; the changed phone-navigation and service pages were checked after the final edits. Setup-card/rear-label files and printed QR destinations were unchanged. The revised manual is prepared locally and has not replaced the hosted copy.

## Exact builds

| Board | Application bytes | Whole-file SHA-256 |
| --- | ---: | --- |
| S3 | 1,399,104 | `ab7a5ce3ead93bfc376b900ff41981379a4c4e663b3d45870a7d8799b35ac7ce` |
| C3 | 1,443,376 | `f0011b13e14a50de08cb8825102d534f1bade923e4e88901fd8f817853071c76` |

Raw backups, board identity, diagnostic evidence, signed packages and browser screenshots remain in ignored local directories. No hosted asset, release feed or repository remote was changed. Previously user-reported physical checks describe beta 6; detailed beta-7 physical/electrical/overnight acceptance remains pending.
