# Dragon Kingdom release verification — 19 October 2026

`v0.2.2-prototype` consolidates the work since the original GitHub publication
and the fixes/diagnostics from live S3 testing. It supersedes 0.2.0/0.2.1.
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
| ESP32-S3 | 1,154,466 | 1,154,608 | 54,988 |
| ESP32-C3 | 1,179,132 | 1,179,280 | 45,944 |

Both upload images fit the actual 1,572,864-byte application partition.

Source fingerprint, unchanged through the final paired builds:
`d49d95e459b38c316db9ba64da96480e7f5b1dcd02e41cb8d9203e486f56db2d`.

Application SHA-256:

- S3: `ae257d57571cb5e37065ef440b6a7fd5ad4482a0cb78ecbb6279ab5ba22b8ff1`
- C3: `84ae7b8df838da10ea595fe84d1ed395d1315b1ef7325ba425fe9d1d93c6e391`

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
C3 remains build-tested only because no C3
board was available.
The final image also includes the transient `testglow` measurement command,
avoids the redundant first STA start/stop, and applies the existing 8.5 dBm
limit before association starts. These connection-path changes did not resolve
all repeated-reset failures; the hardware record retains the failed trials.

External-only supply/current/thermal tests require laptop USB disconnected.
Final prints, photographs and Gerbers, optical fit, C3 carrier orientation and
strapping, longer endurance and power-cut/NTP recovery are still outstanding.

Raw local release evidence is in ignored
`dragon-firmware/.tools/kingdom-release-20261019/`. Paired immutable flasher
bundles are `20261019-kingdom-d49d95e459b3-s3` and
`20261019-kingdom-d49d95e459b3-c3` under `.tools/batch-flash/`.
