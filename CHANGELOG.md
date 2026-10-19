# Changelog

## 0.2.2-prototype — 19 October 2026

- Added transient USB `testglow` measurements below the normal 10% control
  minimum. The user's comparison confirmed raw 10% extinguishes the USB-limited
  pattern while the retained minimal nonzero output is clearly visible.
- Removed the redundant STA start/stop cycle before the first saved-network
  connection. Later connection replacements still stop a pending station.
- Updated the S3 hardware evidence, firmware bundles and developer instructions.

## 0.2.1-prototype — 19 October 2026

- Live S3 testing found that saving/copying a custom dragon could leave the
  previous dropdown selection until polling. Immediate edit/delete now follows
  the newly saved dragon, with a regression test that fails on the old code.
- Dark-room dimming combined with minimum manual glow could round awake pixels
  to black. Dimming now preserves a minimal nonzero level for already-lit pixels;
  sleep, black regions and all session power ceilings remain effective. Native
  checks cover all 79 selectable presets at six power budgets.
- Installed and tested the matching S3 firmware over USB-only power. See the
  [19 October physical record](docs/HARDWARE-TEST-2026-10-19.md). C3 is build-tested;
  no C3 board was available for physical testing.

## 0.2.0-prototype — 19 October 2026

- Renamed the product, offline interface, setup-card template, manual and build
  tools to Dragon Kingdom. The repository is now `sai021/dragon-kingdom`.
  Updated boards advertise `Dragon-Kingdom-XXXXXX`; update older bookmarks and
  setup cards. Existing home Wi-Fi credentials and saved collections survive.
- Added separate ESP32-S3 and ESP32-C3 firmware targets, automatic chip detection,
  checksum-verified paired batch bundles and CI builds/artifacts for both boards.
- Added daily whole-wing sunrise alarms, phone clock/DST synchronization,
  preview/stop, daylight glow and brighter glitter.
- Updated the supplied palette colours and horizontal output orientation;
  retired two entries without changing the 81 stable storage IDs.
- Added stale-form/duplicate-save protection, alarm-load recovery, explicit busy
  controls, empty-profile recovery, bounded HTTP and safer Wi-Fi transitions.
- Added USB diagnostics/provisioning, assembly diagnostic sketches, expanded
  native/browser/Python checks and consolidated physical test evidence.
- Retained network-event locking, protected All, saved-data migration and the
  estimated 400 mA computer-USB ceiling. Earlier CAD/PCB/optical files remain
  prototypes pending the user's newer files and assembly evidence.

See [release verification](docs/KINGDOM-RELEASE-2026-10-19.md) for exact build
hashes, test results and physical coverage limits.

## 0.1.0-prototype — 15 October 2026

Initial consolidated project checkpoint for Dragon Kingdom.

- ESP32-S3 touch/ambient controls, 81 supplied palettes and bounded animations.
- Offline phone interface, Wi-Fi provisioning, retry and deliberate setup recovery.
- Protected All, three named profiles, filtered collections and ordered favourites.
- Eight persistent custom dragons with independent region colour/effect editing.
- Creation copy/delete, profile deletion retaining creations in All, and checked
  alternating storage snapshots.
- Fixed reproduced networking startup crash with the core's event callback lock.
- Retained laptop USB's 400 mA estimated ceiling and the separate deployed
  external-supply arrangement.
- Consolidated developer/parent guides, architecture/API, provenance and test status.
- Preserved earlier optical/CAD sources and reviews as prototype history.

Newer printed STL designs, making-of photos and final Gerbers are awaiting the
user's later delivery. Weather, parent PIN, lost-card recovery, portable backup
and web firmware updates are not part of this checkpoint.
