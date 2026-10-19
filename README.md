# Dragon Kingdom

A touch-controlled dragon lightbox for one child, with a phone interface for
the child and their parents. An ESP32-S3 or ESP32-C3 drives an 8×8 RGB LED
matrix behind a dragon face.
Families can pick dragons, play lighting effects, save personal collections,
and make custom dragons without installing an app or writing code.

**Current state: working development prototype, firmware 0.2.4, updated 19 October 2026.**
The [Dragon Kingdom release](docs/KINGDOM-RELEASE-2026-10-19.md) consolidates the
accumulated source, interface, asset, palette and documentation improvements.
Separate S3/C3 firmware downloads, checksums and the manual are on
[GitHub releases](https://github.com/sai021/dragon-kingdom/releases/tag/v0.2.4-prototype).
The [keeper edition](docs/KEEPER-EDITION-2026-10-19.md) adds a dragon-only colour
editor, working favourites search and an eight-page keeper manual
(edition 0.6) using the confirmed enclosure layout. Both boards are built; the
updated C3 embedded interface is physically checked. Earlier 0.2.3 board tests
remain recorded separately below.

Updated setup Wi-Fi and `.local` names use `Dragon-Kingdom-XXXXXX`; update old
bookmarks/setup cards. Saved collections, alarms and home Wi-Fi remain compatible.

Both 0.2.3 board images were installed and physically tested under laptop
USB-only power. Each passed five Wi-Fi reconnect/HTTP trials and a real cold
USB boot, alongside live embedded web controls and saved-data checks. The user
confirmed C3 touch gestures, lighting and LDR response on 0.2.3. The physical
checks also found and fixed immediate custom selection, minimum-glow rounding
and the [radio startup/power-setting race](docs/WIFI-READINESS-2026-10-19.md).
Software checks passed: 25 Python tests, 15 native suites, simulated browser
workflows and both pinned firmware builds. Physical and simulated evidence are
recorded separately in the [hardware record](docs/HARDWARE-TEST-2026-10-19.md).

**Remaining acceptance work:** earlier S3 reconnect failures and an unexplained
reset-helper error remain recorded. The later S3 passes used a clearer antenna
position and ROM-only reset procedure; they do not prove the cause or broader
reliability. Range/endurance, physical phone browser coverage, deployed external
supply/current/thermal behaviour and final PCB/mechanical/optical fit remain
open. The user confirms the hardware is made, with a right-side touch button, rear
keyhole mounting slot and bottom USB-C power port; the internal controller USB
port is inaccessible to users. Existing CAD/PCB assets are earlier prototypes;
newer user-supplied files are still pending.

## What works

- Tap for the next dragon, double tap for sleep/wake, hold for brightness.
- 79 selectable supplied dragon palettes (81 stable storage slots), plus eight saved custom creations.
- Four profiles: protected **All** and three named collections.
- Named profiles show favourites plus their own creations; physical taps use
  the same collection. Empty profiles invite you to add or create dragons.
- Profile deletion preserves its creations by moving them into All.
- A phone editor for ten regions, including separate wing edges and interiors.
  Untouched regions retain imported pixel variations. Save, copy and delete
  creations, with rainbow, breathing, shimmer and glitter by region.
- One-button glitter, fire, breathing and rainbow, glow control and sleep/wake.
- On-device Wi-Fi setup, nearby network search and saved home-network details.
  Everyday play does not require internet or an account.
- Automatic ambient dimming and startup selection of an estimated power ceiling.
- Daylight lighting stays on; a saved daily sunrise alarm gradually brightens
  the wings toward a chosen wake-up time, with a phone preview and stop control.

Weather animations, a parent PIN, firmware updates through the web interface,
and export/import backups are not implemented yet.

## Start here

| Reader | Guide |
| --- | --- |
| Parents testing a prepared device | [Phone and touch guide](docs/PARENT-GUIDE.md) |
| Child and grown-ups | [Printable user manual](output/pdf/dragon-kingdom-user-manual.pdf) / [editable text](docs/USER-MANUAL.md) |
| Developers setting up another computer | [Build and test](docs/DEVELOPMENT.md) |
| Continuing live device and web testing | [Testing handover](docs/TESTING-HANDOVER.md) |
| Hardware assembly and power | [Hardware wiring](dragon-firmware/HARDWARE-WIRING.md) |
| Profiles and custom dragons | [Collections and editing](dragon-firmware/PROFILES-AND-CREATIONS.md) |
| Wi-Fi setup and recovery | [Web setup](dragon-firmware/WEB-SETUP.md) |
| Current manual edition | 0.5, 19 October 2026; eight A4 pages |
| Current evidence and unfinished checks | [Project status](docs/PROJECT-STATUS.md) |
| System design and API | [Architecture](docs/ARCHITECTURE.md) |
| Optical/CAD prototype | [Mechanical assets](docs/MECHANICAL-ASSETS.md) |

## Power arrangement

During development, laptop USB-C powers the connected circuit through the
ESP32 USB connector. **External/main power must remain disconnected.** When a
computer USB host is detected, firmware retains a 400 mA **estimated** session
ceiling. This is a model-based limit, not USB power negotiation or a current
measurement.

In the deployed product, the external product supply powers the matrix
directly through the shared 5 V rail. The ESP32 board/USB connector is not the
intended matrix power source. Disconnect laptop USB before external-only tests.
Never connect both powered inputs simultaneously with the current circuit.

## Repository map

```text
docs/                         consolidated project and parent guides
dragon-firmware/
  DragonPrototype/            Arduino sketch, renderer, storage, web API
  web/                        editable offline phone page and editor
  presets/                    editable supplied dragon catalog
  tools/                      build, import, desktop editor and test helpers
  tests/                      native C++, Python and browser checks
  hardware/                   CAD sources, exports and dated Gerber reviews
dragon-masks/                 registered optical masks and artwork references
  light-guide/                canonical mesh build/check scripts and reports
dragon-light-guide-prototype/ legacy delivery notes and validation reports
```

Local runtimes, firmware binaries, logs, device credentials, printable setup
cards, generated large STL meshes, and duplicate ZIP bundles are excluded
from Git. See [mechanical assets](docs/MECHANICAL-ASSETS.md) to rebuild the mesh.
Nothing is deleted from the local workspace by these exclusions.

## Reproduce the firmware

Install Python 3 and Arduino CLI, then run from `dragon-firmware`:

```sh
python tools/dev.py setup
python tools/dev.py build
python tools/dev.py ports
python tools/dev.py upload --port YOUR_PORT
```

Use the actual detected port, not a port copied from a test log. Close serial
monitors before uploading. Build uses Arduino-ESP32 3.2.1, Adafruit NeoPixel
1.12.5, 4 MB flash, 2 MB PSRAM and the supplied custom partitions.

To program several boards, double-click `dragon-firmware/Flash Dragons.cmd`.
The [batch flasher guide](docs/BATCH-FLASHING.md) covers building once,
swapping boards, and manual Boot/Reset steps.
The flasher supports mixed S3/C3 batches by reading the connected chip identity
and choosing a separate saved firmware image. C3 uses the matching eight-pin
header map. A C3 on the carrier has now passed published-image USB startup,
library and 400 mA ceiling checks, plus user-confirmed lighting, touch gestures
and LDR response. Cold USB boot, live web workflows and three Wi-Fi/HTTP reset cycles also passed;
startup with touch held and setup-Wi-Fi visibility also passed.

The build regenerates palette and embedded-page headers. Keep
`DragonPrototype/build_opt.h`: its network-event locking fixed a reproduced
startup crash in this pinned core. Full instructions and tests are in
[DEVELOPMENT.md](docs/DEVELOPMENT.md).

## Provenance

See [asset and dependency notes](docs/PROVENANCE.md). No blanket licence is
being applied to supplied character palettes, artwork, or third-party CAD
symbols. Their existing notices and provenance are retained.
