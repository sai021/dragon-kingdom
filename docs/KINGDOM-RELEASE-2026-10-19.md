# Dragon Kingdom release verification — 19 October 2026

`v0.2.3-prototype` consolidates the work since the original GitHub publication
and the fixes/diagnostics from live S3 testing. It supersedes 0.2.0–0.2.2.
The [Wi-Fi readiness repair](WIFI-READINESS-2026-10-19.md) waits for the station
start event and checks the existing radio limit before association. Physical
status confirmed the old image could report 20 dBm instead of the intended
8.5 dBm. Correcting this setting did not eliminate every reconnect failure.
**Physical acceptance remains open:** repeated S3 resets exposed intermittent
home-Wi-Fi authentication/reconnection failures. Some starts work; this is not
a final reliability sign-off.
The repository is [sai021/dragon-kingdom](https://github.com/sai021/dragon-kingdom).
This is a development prototype checkpoint; software checks do not complete
the remaining physical product verification.

## Name and update compatibility

The phone page, documentation, printable manual, package metadata, flasher,
setup-card template and associated filenames now use Dragon Kingdom. The
editable page is `dragon-firmware/web/dragon-kingdom.html`; its embedded header
was regenerated. The manual is `output/pdf/dragon-kingdom-user-manual.pdf`.

Setup Wi-Fi and mDNS now use `Dragon-Kingdom-XXXXXX`. Replace old `.local`
bookmarks and setup cards after updating. The device's numeric address is still
shown in its page. Home-network credentials, library storage keys, stable
catalog IDs, profile zero (All), migration behaviour and alarm storage are
unchanged. The shared setup/browser key remains `dragon123`, username `parent`.
Reload the page after updating so forms use the current save context.

Earlier CAD, Gerbers, optical masks and supplied artwork retain their provenance
and prototype status. No geometry or missing final design was invented during
the rename. Private captures, credentials, runtimes and generated large meshes
remain ignored. Previous immutable firmware/test evidence remains local history.

## Software verification

| Check | Result |
| --- | --- |
| Python regressions | All 25 passed, including catalog/editor and paired flasher publication |
| Native C++ | All 15 suites passed, including C3 pin/USB simulation, alarm, storage and bounded HTTP |
| Browser simulations | Passed at 390 × 844 in headless Edge, including busy controls, initial alarm recovery, stale drafts and empty-profile reload |
| Printable manual | Eight A4 pages rebuilt, all rendered pages visually reviewed; title, headings and page numbers checked |
| Source generation | Palette and embedded page generated from editable sources |
| Firmware builds | Both targets compiled using Arduino-ESP32 3.2.1 and NeoPixel 1.12.5 |
| Release packaging | Paired bundle published atomically, loaded back and checksums verified; both download ZIPs reopened and verified |

The 400 mA estimated computer-USB ceiling and network-event lock remain intact.
Tests using native fakes and simulated HTTP are separate from device tests.

| Target | Compiler application bytes | Upload image bytes | Static RAM bytes |
| --- | ---: | ---: | ---: |
| ESP32-S3 | 1,154,842 | 1,154,992 | 54,988 |
| ESP32-C3 | 1,179,362 | 1,179,504 | 45,944 |

Both upload images fit the actual 1,572,864-byte application partition.

Source fingerprint, unchanged through the final paired builds:
`4c20fe7d4d16b924a49b54e342d2961e48a941ce924a926b80609bcee3dc2496`.

Application SHA-256:

- S3: `ceaf3b1eddc8932e7fe1534dccc9764d9c2b78544d574aef5885f7cd9f914a98`
- C3: `bb3c18307bf958fd6aa86aa771b3c7b2937a33193f21d351d83271e2f9858a80`

Each board-specific release ZIP includes its application, bootloader, partition
table, pinned `boot_app0.bin`, flashing instructions and a hash/offset manifest.
Images are kept as release downloads rather than tracked binaries. The upload
instructions write separate regions and do not erase NVS. Do not flash a merged
whole-flash image over existing saved data. The normal source build/batch flasher
remains the recommended workflow. CI now retains separate S3/C3 build artifacts.

## Physical verification status

The user confirmed laptop USB-only power and S3-only availability. The S3 was
ROM-identified, its NVS backed up privately, and both the initial and corrected
images installed with flash hash verification. Live startup, API/persistence,
browser and transport checks are recorded in the
[19 October physical record](HARDWARE-TEST-2026-10-19.md). Those checks exposed
and led to fixes for immediate custom selection and minimum-glow rounding.
The corrected S3 image passed the embedded UI workflows, including immediate
copy/edit/delete. Physical touch/LDR activity was recorded; the user confirmed
tap/double-tap and that minimum glow remains lit with the LDR covered.
A C3 was subsequently connected on the carrier with user-confirmed pin
orientation. Its published 0.2.2 image is installed with flash hash verification
and passed USB startup/library/400 mA checks. User-confirmed visible lighting,
tap, double-tap, hold brightness and LDR response agree with captured telemetry.
Cold USB boot, live embedded-page workflows and three saved-Wi-Fi/HTTP
reset cycles also passed. Startup with touch held also passed: the user confirmed normal lighting and
phone visibility of setup Wi-Fi; post-boot serial and HTTP confirmed AP active,
home Wi-Fi connected and the retained USB ceiling.
The final image also includes the transient `testglow` measurement command,
avoids the redundant first STA start/stop, and applies the existing 8.5 dBm
limit before association starts. These connection-path changes did not resolve
all repeated-reset failures; the hardware record retains the failed trials.

External-only supply/current/thermal tests require laptop USB disconnected.
Final prints, photographs and Gerbers, optical fit,
longer endurance and power-cut/NTP recovery are still outstanding.

Raw local release evidence is in ignored
`dragon-firmware/.tools/kingdom-release-20261019/`. Paired immutable flasher
bundles are `20261019-kingdom-4c20fe7d4d16-s3` and
`20261019-kingdom-4c20fe7d4d16-c3` under `.tools/batch-flash/`.

The current S3 image is 0.2.3; its radio-setting correction and mixed reset
results are detailed in the linked readiness repair. The C3 physical results
above apply to 0.2.2. The updated 0.2.3 C3 image is build-tested only.

Latest S3 placement follow-up: five ROM-only resets rejoined and served HTTP
in 7.4–8.6 seconds each, and a manual cold USB boot connected at about 7.6
seconds uptime. These passes are limited to the tested clearer antenna
position; earlier failures and an unexplained helper/reset error remain
recorded. The updated C3 physical check is pending.
