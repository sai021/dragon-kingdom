# Reliability repairs — 19 October 2026

The nine software findings in the [18 October audit](RELIABILITY-AUDIT-2026-10-18.md)
are addressed, along with the HTTP transport stall risk and Wi-Fi join
cancellation. The intended product has one child using it; saved profiles
remain optional collections. The request safeguards handle an outdated page,
an interrupted save or another tab without adding a multi-user system.

These are source, build and simulated-test results. No board was flashed,
reset or connected to a serial monitor during this repair session. The installed
device state and physical observations in the earlier handover describe its
previous firmware. Current household credentials and device records were not
read or changed.

## Repairs

| Audit item | Implemented behaviour | Regression evidence |
| --- | --- | --- |
| R1: wrong-profile writes | Collection writes require the profile and generation loaded by the form. Missing, stale and malformed context receives HTTP 409 before any write. Custom drafts retain their original context. | Actual library route tests cover stale forms, valid writes, deletes, protected All and duplicate creation retries after a lost response. Browser tests retain a rejected draft. |
| R2: shifting custom IDs | The 81 supplied IDs/order are fixed by `presets/catalog-ids.json`; validation rejects additions, removals, renames and reordering. A firmware assertion also rejects changed slot count. The legacy clone command fails before saving. | Catalog compatibility tests cover all four changes. Existing custom records and retired preset bases still load. |
| R3: alarm-load failure | Initial failures are retried. Save and alarm fields wait for an authoritative load; successful clock sync can also populate the complete saved form. Polling preserves later edits. | Browser tests inject repeated initial failures and verify enabled / 06:05 / 35-minute values recover correctly. |
| R4: misleading busy controls | Conflicting controls disable during a command, with a waiting message. A refused synthetic profile change also restores the actual selection. | Browser tests hold a play response, check disabled controls and inject a profile change. |
| R5: mixed build revisions | Both targets stage and validate before one atomic `current-set.json` publishes the pair. It records a source hash and per-file checksums. Failure on either target retains the previous complete pair. Legacy single-target selections remain readable. | Tk/temporary-bundle tests fail the second compiler after S3 succeeds and verify unchanged selections and manifest bytes. |
| R6: infeasible 300 mA budget | The 300 mA fallback keeps Wi-Fi off and retains touch lighting. Rendering and diagnostics use the same controller/radio reserve calculation. USB remains capped at an estimated 400 mA. Serial network operations also reject unavailable networking. | Native power, custom-rendering and sunrise checks include every applicable reserve without an idle-panel exemption. |
| R7: colour fixture blocks tests | Current catalog checks enforce storage identity, structure and valid pixels. Historical colour assertions use the dated audit record, allowing later editor changes. The runner reports independent failures and continues to other suites. | All Python tests pass with the existing edited colours. |
| R8: empty-profile reload | Control availability is derived from the loaded collection, including before the first response and after full reload. | Browser reload of an empty named profile keeps dragon/glow controls disabled. |
| R9: C3 absent from CI | Firmware CI uses an S3/C3 matrix. Python, native and browser checks run independently. Browser installation uses a generated npm lockfile. | Workflow structure checked locally; both Arduino targets built locally. No remote CI run was triggered. |

The single-child scope does not require removing useful collections or changing
the saved-data format. Profile zero remains protected All; deleting a profile
still retains its creations. The existing snapshot migration/checksum behaviour,
network-event locking, Wi-Fi TX setting and separate alarm storage are retained.

## Bounded HTTP and Wi-Fi changes

`HttpRequestPolicy.h` and `BoundedWebServer.h` bound the transport work around
the pinned Arduino-ESP32 3.2.1 parser. Incoming bytes accumulate without blocking,
including fragmented TCP packets. A complete supported request is parsed from
memory, with its existing authentication, route validation and form decoding.

Headers are limited to 2,048 bytes and bodies to 1,536 bytes. Requests have a
three-second whole-request deadline. Unsupported multipart/chunked framing,
duplicate lengths, unframed trailing bytes and oversized requests are rejected.
Responses are limited to 64 KiB, sent with nonblocking socket writes in chunks
of at most 1,024 bytes per update and a five-second send deadline. A build
assertion keeps the embedded page below the response capacity.

Wi-Fi interface changes wait for the queued reply. Forget and connection-timeout
paths stop the station interface and automatic reconnect, rather than relying
on `disconnect()` while association is still pending. Setup AP recovery and
save-only-after-success behaviour remain intact.

The new native HTTP suite covers small fragments, maximum-size bodies, partial
and trickling requests, conflicting lengths, oversized requests/responses, slow
readers, short writes, disconnection and timer rollover. It uses a fake socket
and server facade. Both real Arduino builds verify the adapter against the
pinned core headers and protected parser API. Live radio/HTTP behaviour still
needs device verification; dependency upgrades must retest this adapter.

## Final verification

| Check | Result |
| --- | --- |
| Python regressions | 25 passed, including Tk flasher and catalog/editor checks |
| Native C++ | All 15 suites passed, including actual library routes and bounded HTTP |
| Browser simulation | Passed the existing workflows and new failure/recovery cases at 390×844 with Playwright 1.62.1 and headless Edge |
| Clean locked Node dependency installation | `npm ci` succeeded; browser suite passed with that installation |
| Python syntax / CI structure | Passed; independent test groups and both target builds configured |
| Editable palette file | Preserved byte-for-byte, including the current default and colour edits |
| Persistent library layouts | Profile, Custom and Data definitions unchanged |
| Generated product headers | Regenerated through the normal source generators/builds |
| Source consistency | Both final builds used the same fingerprint; unchanged through publication |
| Saved release | Both targets published together and loaded back with matching checksums |

| Target | Compiler app usage | Upload image bytes | Static RAM |
| --- | ---: | ---: | ---: |
| S3 | 1,153,906 | 1,154,048 | 54,980 |
| C3 | 1,178,486 | 1,178,624 | 45,944 |

Both upload images fit the actual 1,572,864-byte application partition. Static
RAM includes the bounded request buffer. The response buffer uses heap memory
with a fixed upper bound and rejects allocation failure; this still needs live
free-heap and repeated-request observation.

Source fingerprint:
`3d49c3844e6d65ea4471b9519870587bf91f343d3f61f126d52273e79a12113f`.

Application SHA-256:

- S3: `4113ade4072cc6420b077a352a8d426fa14d78aad320d21987d6ca23fae933e6`
- C3: `b358d4c6cb6633663ba7bd88b1ebe33cd914e76e4323595120d4b32d75caa3e3`

The flasher now selects the paired release through ignored
`.tools/batch-flash/current-set.json`:

- `20261019-reliability-3d49c3844e6d-s3`
- `20261019-reliability-3d49c3844e6d-c3`

Previous immutable images and legacy selection files remain available locally.
Logs, pre-repair source copies, build results and publication evidence are in
ignored `.tools/reliability-fixes-20261019/`. No credentials or large generated
meshes were added to the repository.

## Documentation and live follow-up

Architecture/provenance notes now describe the shared access key, 60-second
connection timeout, alarm records/routes, current optical-map discrepancy and
bounded transport. The catalog guide describes the fixed IDs, and the batch
guide describes paired publication. The installed-preset helper requires the
current port, uses DTR with RTS inactive and checks startup before selecting
test dragons. It was not run on hardware during these repairs.

After installing this build, reload any old browser page. Its old collection
forms lack the new request context and will correctly receive HTTP 409.

The next device session should verify normal setup/authentication, custom
save/delete and reset persistence, scan/join/wrong-password recovery, forgetting
an in-progress join, and sustained page polling while using touch. Include
fragmented/incomplete requests and a slow response reader while observing loop
responsiveness, heap, sunrise progress and uptime. Then run router-loss and
power-cut/NTP recovery checks. These are pending physical tests, not results of
the native/browser simulations.

C3 hardware, deployed supply/current/thermal behaviour, final prints, optical
fit and updated Gerbers remain separate work. The older R4 pad-entry correction
and firmware/optical-map discrepancy are preserved for the final design review.
Use laptop USB and external/main power mutually exclusively in the current
circuit; no electrical limit was raised by these changes.
