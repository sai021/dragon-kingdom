# Keeper edition — 19 October 2026

Firmware `v0.2.4-prototype` adopts the keeper-edition suggestions supplied by
the user, with a dragon-only editor and manual edition 0.6. Weather and OTA
remain deferred. Original draft files are retained locally as reference;
the maintained sources are `dragon-firmware/web/` and `docs/USER-MANUAL.md`.

## Editor and interface

The custom editor presents selectable dragon regions without LED-grid views,
overlays or view switches. Taps select the visible shape; empty space leaves
the selected part unchanged. The part dropdown provides an alternative.
The illustration uses representative colours from the original region pixels;
untouched saved markings and the existing colour/effect masks are preserved.

Favourites search hides unmatched rows, retains checked favourites outside the
filter and reports empty results. CSS now respects the HTML hidden attribute.
The create button changes to “Edit or copy custom dragon” for custom selections,
including immediately after saves. Ordinary play and error labels stay clear,
with keeper language in supporting copy. No firmware power, radio, gesture,
alarm, library-storage or network-locking logic changed.

## Confirmed enclosure and manual

The user confirms that the hardware is made: touch button on the right side,
USB-C power port at the bottom, keyhole-shaped mounting slot on the back, and
the motto around the dragon except along the bottom. The internal ESP32 USB-C
connector is inaccessible to normal users. Newer STL files, photographs and
Gerbers remain to be supplied; existing repository CAD/PCB files are earlier
prototypes and must not be relabelled as the updated manufactured design.

The keeper manual uses those physical details and the current control labels.
It removes the pretend training-time restriction, LED-grid instructions and
the guarantee of a fixed visible 10% night glow. Normal power and setup guidance
stays explicit. Edition 0.6 was rebuilt as eight A4 pages; all eight rendered
pages were visually inspected, including page numbering and the certificate.

## Verification and builds

- All 25 Python tests and 15 native suites passed.
- The simulated browser suite passed, including all nine illustrated-part hits,
  background taps, untouched markings, actual visible search filtering,
  retained selections, custom save/copy/delete and existing recovery workflows.
- The alarm-error test fixture now holds simulated failures until explicitly
  released, avoiding a race with automatic polling rather than weakening checks.
- Both pinned firmware targets compiled, fit the existing 1,572,864-byte app
  partition and were packaged atomically with verified ZIP contents/checksums.
- The connected C3 was ROM-identified, its NVS backed up privately, and the
  published keeper image installed with flash hash verification. Startup
  retained All, zero customs, generation 16 and the 400 mA USB ceiling. Saved
  home Wi-Fi connected. Actual embedded-page checks passed authentication,
  glow, sleep/wake, alarm save/reload/restore and preview/stop, Wi-Fi scan,
  protected All, empty-profile reload, custom save/copy/delete, favourites and
  profile-deletion rehoming. New checks passed visible filtering across all
  79 presets, no grid controls, and all nine illustrated body-part selections.
  Temporary test data was removed; only All, zero customs, Blue/100% glow and
  the original disabled alarm remain. These are live-device desktop checks,
  not physical-phone tests. An initial test attempt omitted reopening a
  collapsed settings section after reload; its cleanup ran, and the corrected
  test then passed. No product change was needed for that harness error.
- The S3 keeper image is build-tested; prior S3 physical results apply to 0.2.3.
  Earlier S3 Wi-Fi/reset anomalies remain documented separately.

| Target | Compiler app bytes | Upload image bytes | Static RAM bytes |
|---|---:|---:|---:|
| S3 | 1,161,114 | 1,161,264 | 54,988 |
| C3 | 1,185,642 | 1,185,792 | 45,944 |

Paired source fingerprint:
`68652e418c758894e70e3cd7836d67ed6f33e006b25a2cd9c88f94d2bd80a7ae`.

Application SHA-256:

- S3: `e0e095cd68e1a645aae0ea6e3fc1bdfae433a820c15b47a1bce76ef1ed03d50b`
- C3: `4e2fb781c532ae4aec30b381b5089d4ee6b3b106f5470cc54e747f91dba52a2c`

Immutable bundles are `20261019-kingdom-68652e418c75-s3` and
`20261019-kingdom-68652e418c75-c3` in the ignored firmware cache. Captures,
settings backup, logs and packaged downloads remain under ignored
`dragon-firmware/.tools/keeper-edition-20261019/`.

Layout confirmation and desktop-browser checks do not complete external-supply,
current/thermal, optical, physical-phone, range or endurance validation. Keep
laptop USB and external/main power disconnected from each other throughout
development testing; never power both inputs together in the current circuit.
