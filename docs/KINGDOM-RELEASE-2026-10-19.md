# Dragon Kingdom release verification — 19 October 2026

`v0.2.1-prototype` consolidates the work since the original GitHub publication
and the fixes found during live S3 testing. It supersedes 0.2.0.
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
| ESP32-S3 | 1,153,982 | 1,154,128 | 54,980 |
| ESP32-C3 | 1,178,566 | 1,178,704 | 45,944 |

Both upload images fit the actual 1,572,864-byte application partition.

Source fingerprint, unchanged through the final paired builds:
`d81491378cb7872d56f08ec0d532e6650d83e6924e0a57b12e2ebf58fb6fcc4a`.

Application SHA-256:

- S3: `b6d03d2cfbf049dd7b099b4c2ea186e7cbd17659db971042550b43cab50ec8ef`
- C3: `9f05d31e170ff973647085df919c67f1c56ae6f5801492f160025a11c457b339`

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

External-only supply/current/thermal tests require laptop USB disconnected.
Final prints, photographs and Gerbers, optical fit, C3 carrier orientation and
strapping, longer endurance and power-cut/NTP recovery are still outstanding.

Raw local release evidence is in ignored
`dragon-firmware/.tools/kingdom-release-20261019/`. Paired immutable flasher
bundles are `20261019-kingdom-d81491378cb7-s3` and
`20261019-kingdom-d81491378cb7-c3` under `.tools/batch-flash/`.
