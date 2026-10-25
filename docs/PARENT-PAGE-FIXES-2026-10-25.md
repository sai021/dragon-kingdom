# Parent page and GitHub download fixes - 25 October 2026

The corrected C3 was updated over Wi-Fi from beta 4 through diagnostic beta 5 to beta 6. Laptop USB remained disconnected per the user's confirmation. Source commits: `cee5457` (page fixes and diagnostics), `69ba10a` (bounded long-redirect fix, tests and beta-6 identity). Existing beta-4/5 signed sets were preserved; nothing was published.

## Changes

- Applied the compact checkbox layout to Return to Release and rotation. Kept the checkbox beside its label and verified its actual 22 by 22 pixel geometry in the browser suite.
- Added space between support/backup actions and before Parent settings headings.
- Used the current access-point state to distinguish an active home-network handover from a completed connection.
- Explained file upload on either home Wi-Fi or setup Wi-Fi, without requiring an unnecessary network switch.
- Distinguished room-light calibration in user backups from the chip-bound voltage-divider calibration, which is excluded.
- Added parent-only, numeric HTTPS failure diagnostics: transport/TLS/socket errors, clock, free heap and largest block. No network names, credentials or tokens are included.
- Fixed the GitHub request-buffer bound. Real GitHub redirects were approximately 915 bytes; their request line was approximately 886 bytes, exceeding the old 512-byte TX buffer. ESP-IDF's request-line builder returns -1 before sending when this buffer is insufficient, which was incorrectly presented as a verified-HTTPS failure. The TX buffer is now 1,152 bytes for the existing 1,024-byte URL capacity. Overlong redirects are rejected explicitly instead of truncated. Trusted-host restrictions, certificate verification, firmware signature checks and OTA chunk bounds remain intact.
- Older published manifests now produce a clear "No compatible online release has been published" message and remain ineligible for installation.

The request-line requirement was confirmed against [Espressif's HTTP client implementation](https://github.com/espressif/esp-idf/blob/v5.4.1/components/esp_http_client/esp_http_client.c), alongside live failure telemetry with no TLS verification flags and a successful desktop reproduction of the redirect chain.

## Verification

59 Python tests, 18 native suites, the phone-sized browser workflow and fresh pinned S3/C3 builds pass. New tests exercise the actual transport adapter with deterministic HTTP/RTOS fakes: long signed redirects, oversized redirects, untrusted hosts and TLS diagnostic capture. These transport tests simulate TLS rather than implementing cryptography. The real C3 then fetched the GitHub metadata successfully with certificate verification enabled and all HTTPS error fields zero.

The first beta-6 upload timed out part way through and was not finalized; beta 5 remained reachable. Retrying the signed package completed in approximately 167 seconds. After restart the device reported beta 6, C3, VALID OTA state, startup validation complete and divider calibration present. Persistent library, rotation, room-light and alarm enabled/time/duration fields compared unchanged. RAM-only clock/timezone rules were excluded from the persistence comparison, as established in the earlier physical record.

The final live browser showed the compact checkbox, improved spacing, completed home-Wi-Fi wording and corrected upload guidance. Both Release and Beta checks reached GitHub and correctly reported the older published metadata as incompatible; no online install was offered. Local update packages remain available for this candidate. Publication/channel migration is a separate action.

## Exact beta-6 builds

Arduino ESP32 3.2.1 and NeoPixel 1.12.5; source commit `69ba10a5030eaa04855d8bdd82ffa8f43da0d75f`.

| Board | Application bytes | Whole-file SHA-256 |
| --- | ---: | --- |
| S3 | 1,395,632 | `4b3c83df93e27731155d21f8210e2a308c184e8d0e1e6046e2660eb6224c1054` |
| C3 | 1,439,920 | `a677cc1bb2c358a640d2b007ec6f2ee9c2680e79535581cc3d28f151175cba67` |

Both images fit the 1,572,864-byte OTA slot. Compiler static RAM: S3 62,964 bytes; C3 53,920 bytes. Signed immutable packages and private live evidence remain in ignored local directories. The C3 reports calibration presence over Wi-Fi; its raw correction record and exact multiplier were not read back over USB.

Physical LED/touch/LDR checks, actual phone browsers, router outages, full online firmware installation, rollback, restore interruption, USB recovery, S3/ordinary-C3 acceptance and overnight operation remain separate pending gates. No finished-product acceptance is inferred from this page/update test.
