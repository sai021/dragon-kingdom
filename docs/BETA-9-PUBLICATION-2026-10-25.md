# Beta 9 publication - 25 October 2026

**Subsequent S3 issue:** the restart loop recurred. [Live USB/ROM tests](S3-RESTART-RECURRENCE-2026-10-25.md) supersede the brief no-restart observation below. The published notes now flag it; release assets are unchanged.

Published with the user's explicit authorization as an opt-in prerelease: [v0.3.0-beta.9](https://github.com/sai021/dragon-kingdom/releases/tag/v0.3.0-beta.9). Stable latest remains v0.3.0. The hosted manual and existing Release/Beta discovery assets were not changed. This beta is a manual-download transition release; the release notes describe format-2 packages, deliberately labelled offline legacy bridges, and signed USB recovery.

## Accepted firmware and provenance

The colour correction is source `fc1b770`. Both main lamps run that application. After the user praised the colour accuracy, they reported no restarts. They did not separately confirm the latest power arrangement, so this is not extended external-supply acceptance. The C3 passed signed Wi-Fi startup/settings/calibration checks. The S3 passed USB service with all 20,480 NVS bytes unchanged, expected image/VALID startup, and increasing uptime through 70 seconds at the 400 mA USB ceiling. The earlier S3 external-power restart loop and interrupted uploads remain material historical evidence; see [colour and service record](LOW-LIGHT-COLOUR-2026-10-25.md).

GitHub's first run at fc1b770 exposed a cross-platform generated-gzip comparison failure. Commit `d20760923195a5bbf149a5de56a380381ffab20a` changes only the host check and its test: compare identical C++ and decompressed page content, permitting Python/zlib/OS compression differences while rejecting corrupt CRC and stale content. Rebuilt both pinned targets and asserted that both application binaries are byte-for-byte identical to those installed on the lamps. Prepared a new immutable signed set with d207609 provenance, retaining the original accepted set locally.

| Board | Application bytes | SHA-256 |
| --- | ---: | --- |
| S3 | 1,399,744 | `370caaaad4dfb574142fa1683765e729c5b917b6608a06ae03cc91f0e6e9dd42` |
| C3 | 1,443,920 | `30beaf970ec189641e63bb52d8de10db69e2bd9e523f78cab3231151935e2501` |

## Verification and publication

60 Python tests pass locally. [All five GitHub jobs](https://github.com/sai021/dragon-kingdom/actions/runs/40141555886) passed at d207609: Python, all 18 native suites, browser, S3 build and C3 build. Source is pushed to codex/shipping-reliability; release tag points to d207609. No main-branch merge or stable promotion was performed.

The release has 11 public assets: matching S3/C3 .bin/.manifest/.dragon.json files, two explicitly named legacy-bridge .dragon.json packages of the same calibration-aware applications, current-set.json, signed two-board USB recovery ZIP and SHA256SUMS.txt. Verified RSA signatures, image hashes, capabilities/schema and layouts before upload; extracted and verified the recovery ZIP. Only required three images per board and the signed set plus README are in the ZIP: no merged images, NVS, signing key, credentials or machine paths. Downloaded all 11 staged assets, compared their bytes and verified checksums. After publication, checked public metadata/digests and unauthenticated manifest downloads. Stable latest and old Beta feed asset IDs/digests are unchanged.

Actual phone-platform coverage, router-outage/endurance, overnight, measured optical/electrical/thermal behavior, bootloader rollback and interrupted restore remain separate acceptance work. Publication does not convert pending gates into passes.
