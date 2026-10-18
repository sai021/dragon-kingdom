# Dragon Kingdom release verification — 19 October 2026

`v0.2.0-prototype` consolidates the work since the original GitHub publication.
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
| ESP32-S3 | 1,153,922 | 1,154,064 | 54,980 |
| ESP32-C3 | 1,178,502 | 1,178,640 | 45,944 |

Both upload images fit the actual 1,572,864-byte application partition.

Source fingerprint, unchanged through the final paired builds:
`1cf984615c8ee1bdd316c731e119c2d2d31dd22d8d60a4b735a50ea8e04a250b`.

Application SHA-256:

- S3: `771d7761e71cef440568695bd95d0d4c9128aeda22449a3e9af32edee3bd6e44`
- C3: `49769899a4555a21be4fe6eb9ab1970b4eb73145e3da63e3621d84a772e2ed84`

Each board-specific release ZIP includes its application, bootloader, partition
table, pinned `boot_app0.bin`, flashing instructions and a hash/offset manifest.
Images are kept as release downloads rather than tracked binaries. The upload
instructions write separate regions and do not erase NVS. Do not flash a merged
whole-flash image over existing saved data. The normal source build/batch flasher
remains the recommended workflow. CI now retains separate S3/C3 build artifacts.

## Physical verification status

Serial discovery found an Espressif USB device on COM17. Enumeration alone does
not identify S3 versus C3 or prove the power arrangement. Current USB-only power
confirmation and which boards are available were requested before live testing.
No board has yet been flashed or exercised for this named release. Therefore,
the new HTTP adapter and this exact firmware pair do not yet have physical
acceptance evidence. Earlier S3 results remain in the
[18 October hardware record](HARDWARE-TEST-2026-10-18.md); they describe older
installed images and must not be substituted for a test of this release.

Next physical steps: confirm external/main power disconnected, identify the
current chip, capture current state/NVS privately, install its matching image,
verify the USB ceiling, authenticated controls, profile/custom/alarm persistence,
protected All, interrupted HTTP responsiveness, reset/reconnection, touch and
LDR behaviour. Preserve user records and remove only newly created test data.
Run the same checks on C3 when that physical board and verified wiring are
available. Visual appearance, phone platforms and touch require observation.

External-only supply/current/thermal tests require laptop USB disconnected.
Final prints, photographs and Gerbers, optical fit, C3 carrier orientation and
strapping, longer endurance and power-cut/NTP recovery are still outstanding.

Raw local release evidence is in ignored
`dragon-firmware/.tools/kingdom-release-20261019/`. Paired immutable flasher
bundles are `20261019-kingdom-1cf984615c8e-s3` and
`20261019-kingdom-1cf984615c8e-c3` under `.tools/batch-flash/`.
