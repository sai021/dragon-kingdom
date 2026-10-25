# Firmware 0.3.1 and desktop updater — 25 October 2026

The owner explicitly requested main firmware publication and reports the S3 is
working without further restarts. This is a new owner observation, not a measured
endurance result or proof of the cause of the earlier USB/power-on resets.
Historical restart and A/B/A comparison reports remain valid evidence.

Firmware 0.3.1 promotes beta 9's application behavior with only CURRENT_TAG changed:
calibration-aware C3 operation, 1–80% automatic night range before current/artwork
limits, balanced low-light colour rounding, collapsed parent settings, power
information and the GitHub long-redirect HTTPS repair. Saved schema remains 1.
No current ceiling, electrical policy, profile protection or network lock changed.

All shipped lamps are beta 3 according to the owner. They need an explicit
format-1 signed bridge once; ordinary format-2 packages are for beta 4+ and future
versions. Both packages contain the same board-matched calibration-aware image.
The desktop app verifies the signed contract before selecting a bridge. Normal
Release discovery follows GitHub's latest firmware release after repair. Application
releases must use `--latest=false` so they never replace that pointer.

The ten-page manual edition 1.0 was published FIRST to the existing printed-QR
address, with stable /update/ and /setup/ help routes. Downloads were marked as
being prepared while implementation was unfinished. The universal class notice
repeats home setup and has separate update, setup and local-control QR codes.

Desktop source is in desktop-updater/. It saves a private local backup before
writing, supports beta-3 and modern local upload protocols, validates RSA signatures
and board identity, checks ambiguous chunk acknowledgements, aborts cancellation
before finalization, and verifies new version, valid startup and persistent settings.
The local HTTP simulator tests are separate from real-device acceptance.

## Publication and physical verification

Firmware source/tag target: 2cb953a5754c2b26ecc5f0b89cf42d1ac9980cb6. All five jobs
passed in CI run 40171877827. Fresh pinned local S3 and C3 builds were prepared
with signed provenance. All 11 downloaded draft assets matched local SHA-256
before the release was published as GitHub latest. The signed legacy and ordinary
public packages were subsequently downloaded and verified through desktop code
for both boards. Windows blocked execution of a newly compiled local native-test
binary via Application Control; no policy was bypassed. All 18 native suites
passed in Linux CI, and all 60 local Python tests passed.

The owner identified the available beta-3 S3 as normal bottom supply only, laptop
USB disconnected. The new updater core performed a real 0.3.0-beta.3 → 0.3.1
Wi-Fi legacy-bridge installation. It saved a private backup before START, reached
100%, checked VALID startup (otaState 2) and compared persistent settings equal.
A subsequent seven-sample support observation over 63 seconds had increasing
uptime from 86,124 to 149,220 ms, no failed samples, and the normal-supply estimated
2,400 mA ceiling. The restart reason was software reset, expected after OTA.
This short observation does not establish overnight/electrical acceptance. The
other C3 and previous S3 were not flashed by this test. Raw backup/logs remain in
ignored local .tools storage; no credentials or personal settings were published.

Desktop tests cover both boards/formats, lost START/chunk/final replies, cancel
at the last chunk, bad password, signature/board/hash/size rejection, rollback,
settings mismatch, URL boundaries and TLS verification. GUI smoke and packaged
launch checks run on Windows x64, Apple Silicon Mac and Intel Mac. The Intel build
uses static OpenSSL to avoid a bundled-library collision. Packaged HTTPS checks
use the bundled Mozilla CA set with developer certificate paths disabled. The
app uses the signed latest-download contract directly, avoiding anonymous GitHub
API rate allowances. App downloads include dependency notices and unmodified LGPL
source plus the app rebuild recipe. Windows app lacks certificate signing and Mac
apps are ad-hoc signed, not Apple notarized; this limitation is stated in the
family guide, with the phone-only alternative.

The manual (10 pages) and class notice (1 page) were rendered and visually checked;
all three notice QR codes decoded to the exact stable update/setup/local-control
addresses. Pages manual bytes were compared with the local final PDF. No messages
were sent to class families; the owner will distribute the printed notice.


Final desktop source/tag target: 203e3e637fbb79ed77a105f80f86244a06770870.
All three jobs passed in CI run 40172898013. Each downloaded ZIP was inspected
for the correct public key, bundled CA, dependency source/notices and absence of
private keys/credentials. The Windows archive passed actual launch and signed
HTTPS-release checks on this PC. All five uploaded application assets matched
prepared bytes before publication. The updater-v1.0.0 release was published with
latest=false; GitHub latest was checked afterwards and still reports v0.3.1.
The family guide now has the three real download buttons and explicit OS trust
limitations. The printed manual/notice URLs did not change.


The real S3 transfer preceded the final CA-bundle/latest-discovery refinements;
the backup/upload/reboot verification engine was unchanged. The final packaged
downloader was independently checked on all three native platforms and again
from the downloaded Windows archive on this PC. Mac UI checks were CI smoke tests,
not a family user's manual interaction test.
