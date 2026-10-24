# System architecture

> This guide describes the installed 0.2.4 prototype. For the new startup, parent
> authentication and update behavior, use the [0.3.0 candidate notes](NEXT-RELEASE.md).

The ESP32-S3 hosts an offline HTML/JavaScript interface and local HTTP API.
The phone controls the device directly over its setup access point or the home
LAN. There is no cloud backend, remote-control service, child account or audio
pipeline. Internet access is currently unused by animations. Optional NTP supplies UTC
for the sunrise alarm; phone clock sync also works offline. The intended product
has one child using it, with optional saved collections.

```mermaid
flowchart LR
  Phone[Phone browser] --> Web[Local HTTP API]
  Touch[Touch sensor] --> State[Shared lighting state]
  Web --> State
  Library[Profiles and creations in NVS] --> State
  LDR[Ambient sensor] --> Gains[Ambient and touch gains]
  State --> Renderer[64-pixel renderer]
  Power[Startup power ceiling] --> Renderer
  Renderer --> Gains
  Gains --> Matrix[RGB matrix]
```

## Firmware responsibilities

| File | Responsibility |
| --- | --- |
| `DragonPrototype.ino` | Startup, shared lighting state, renderer, touch and serial control |
| `DragonCore.h` | Logical layout, wiring transforms, RGB and current-estimate primitives |
| `SensorControl.h` | Ambient thresholds, hysteresis and touch gestures |
| `StartupPower.h`, `PowerPolicy.h` | Startup sweep, diagnostic records and output limiting |
| `ConnectionPolicy.h` | Setup gesture, retry/inactivity timing, per-device name suffix |
| `DragonLibrary.h` | Profile membership, creations, checksummed alternating snapshots |
| `DragonWeb.h` | Authentication, Wi-Fi, captive DNS, state and play API |
| `LibraryWeb.h` | Profile and creation API validation |
| `DragonPresets.h` | Generated catalog; edit `presets/dragons.json` instead |
| `DragonWebPage.h` | Generated embedded page; edit `web/` instead |
| `build_opt.h` | Enables network event callback locking across the build |

## Persistent state

| NVS namespace | Contents |
| --- | --- |
| `dragon-wifi` | Shared device access key and last successfully joined home network |
| `dragon-library` | Active profile, saved glow, favourites, custom region overrides/effects |
| `dragon-light` | Explicit ambient calibration |
| `dragon-alarm` | Checksummed daily schedule and saved phone timezone rules |
| `dragon-diag` | Four retained failed startup sweeps |

Library snapshots contain version, generation and checksum fields. A verified
alternate snapshot is written before live RAM changes. Startup chooses the
newest valid snapshot, with fallback to the previous one. Profile zero is
normalised to protected All when loading or saving. Record layout/catalog-order
changes require a migration; neither is currently a portable export format.

Custom records reference a supplied base dragon and store region colour masks,
colours and region-effect masks, preserving untouched base pixels. Profile
deletion transfers creations to All. A creation can be shared as a favourite;
editing/deleting it requires its owner profile, while other profiles can copy.

## Wi-Fi lifecycle

- No saved network: open the password-protected setup AP.
- Saved network: try joining it; do not open the AP automatically after failure.
- Deliberate power-on touch hold: reopen setup without deleting credentials.
- Connection timeout: 60 seconds; saved-network retry: one minute.
- Configured AP with no joined clients or active connection attempt: close
  after five minutes of inactivity. An unconfigured AP stays available.
- Commit home-network credentials only after association succeeds. This does
  not check internet reachability.

Local HTTP uses browser authentication (`parent` and the setup password).
Mutation requests require `X-Dragon-Request: 1`; ordinary cross-site forms are
rejected. HTTP is not encrypted on the home LAN. There is no port-forwarding,
remote-control or OTA endpoint in this version.

## HTTP API

All routes below require authentication. POST routes also require the custom
request header. Mutation bodies use form-urlencoded fields, not JSON.

| Method / route | Purpose |
| --- | --- |
| GET `/` | Embedded phone page |
| GET `/api/state` | Connection, selected profile/dragon, effect and brightness |
| GET `/api/dragons` | Active profile's play collection |
| GET `/api/dragons?catalog=1` | Complete catalog for editing/favourite selection |
| POST / GET `/api/scan` | Start asynchronous Wi-Fi scan / inspect results |
| POST `/api/wifi` | Join candidate `ssid` and `password` |
| POST `/api/forget-wifi` | Reopen setup and forget home Wi-Fi |
| GET `/api/library` | Profiles, active ID and creation capacity |
| POST `/api/profile` | `create`, `update` or `select` profile |
| POST `/api/delete-profile` | Delete nonzero profile, retaining creations in All |
| GET `/api/dragon-detail?id=...` | Pixel/region editor data and ownership flag |
| POST `/api/custom` | Create or replace a validated custom dragon |
| POST `/api/delete-custom` | Delete an owned creation and remove favourite references |
| GET / POST `/api/alarm` | Read/save daily sunrise settings |
| POST `/api/alarm/clock` | Synchronize UTC and timezone rules |
| POST `/api/alarm/preview` / `/api/alarm/stop` | Preview or dismiss sunrise |
| POST `/api/play` | `dragon`, `effect`, `brightness` or `toggle` action |

## Power and rendering

Networking starts after a passing startup selection with enough budget for
controller, radio reserve and panel idle. The 300 mA fallback keeps Wi-Fi off
and retains touch play. Computer USB caps
the session at an estimated 400 mA. Wi-Fi reserves a further provisional 50 mA
from the LED budget. Every animation uses channel/current limiting before
ambient and touch percentages. This allowance needs measurement on the actual
supply; voltage plus a model is not an actual-current measurement.

Supply ADC sampling stops after startup. Current-run statistics and session
ceiling are RAM-only. Successful boots keep earlier failure history. The
hardware and startup guide contain the precise criteria and limitations.


## Reliability changes — 19 October 2026

Collection mutation requests include the loaded `profile` and `generation`.
The server rejects missing or stale context with HTTP 409; the editor retains
its draft. `/api/library` and `/api/dragon-detail` expose this context. Version-1
NVS records and existing preset/custom IDs remain unchanged.

`BoundedWebServer.h` wraps the pinned Arduino WebServer parser. It waits without
blocking until one complete GET or form-encoded POST is present. Headers are
limited to 2,048 bytes, bodies to 1,536 bytes, and receipt to three seconds.
Chunked/multipart requests, conflicting framing and pipelining are rejected.
Responses are capped at 64 KiB and sent in nonblocking chunks of at most 1,024
bytes per loop, with a five-second send deadline. Wi-Fi interface changes wait
for the queued response. Request failures do not stop local touch or rendering.
This adapter depends on Arduino-ESP32 3.2.1 and needs live-device verification
before changing that dependency.
