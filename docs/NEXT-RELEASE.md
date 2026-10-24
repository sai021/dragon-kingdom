# Firmware 0.3.0 beta 1

This source implements the 24 October 2026 product direction and is published
as `v0.3.0-beta.1` for experienced testers. It is not a stable release; physical
acceptance checks below remain open. The previous published prototype is 0.2.4.

## Everyday use and parent boundary

The embedded webpage is the interface; Bluetooth, NFC and a separate app are not
part of this release. Play, dragon selection, collections, editing, deletion of
individual collections/creations, sunrise and rotation do not require login.
All remains protected, including at the collection API. The setup Wi-Fi password
remains `dragon123`. Parent settings use that same shared value as a deliberate
unlock action.

Device APIs require a parent session for network search, Wi-Fi changes/retry/forget,
backup export, restore, firmware updates and full reset. The parent area itself
opens normally and shows one password form. All controls behind it remain hidden
and inert until the password is accepted; wrong passwords do not reveal them.

The parent password is always **`dragon123`**, the same familiar value as the AP
key. Its purpose is deliberate access to settings, not a private owner identity.
There is no password-change requirement, credential provisioning, USB code or
recovery step. Previously stored custom parent credentials are ignored. The old
password-change endpoint returns 410 after authentication so cached old pages
cannot change it. Normal play, editing, sunrise and rotation remain login-free.

Existing lightweight session handling remains: random 256-bit tokens stay in RAM,
expire after 15 minutes and are revoked by locking, restart or another login.
Reloading the page starts locked. The UI hides controls immediately on Lock,
expiry or a 401 response; server-side token checks independently protect every
sensitive endpoint. Login attempts are spaced by five seconds. No browser Basic-
auth prompt or additional top-level login protects the parent password form.
Custom request headers guard POSTs against ordinary cross-origin form submissions.
Full reset clears saved user data and home Wi-Fi; the parent password remains
`dragon123`. Password entry does not need credential storage or a flash write.

## Network lifecycle

Every normal startup opens the password-protected AP first and attempts saved home
Wi-Fi concurrently. The association/DHCP deadline is 60 seconds. A failed attempt
stops STA and automatic retries for this powered session; the AP remains up.
**Retry home Wi-Fi** explicitly retries saved credentials. Connect can supply a new
candidate; credentials are saved only after joining that actual network.

Success latches for the powered session. The page shows the numeric home address
and `.local` address where reachable and allows a 15-second handover window before
AP shutdown, regardless of phone count. A phone can lose its AP connection during
association because ESP32 AP+STA shares a radio channel; successful delivery of the
address is therefore best-effort. Rejoin home Wi-Fi and try the saved hostname.
If the home connection later drops, neither automatic retry nor reopening the AP
occurs. Power cycling opens setup again. Wi-Fi changes after a successful join
require a power cycle; Forget keeps the AP closed for that successful session.

Wildcard DNS and HTTP redirect probes lead to the unauthenticated landing page.
Phone captive-portal behavior varies: use the printed local-controls QR or manually
open `http://192.168.4.1/` when needed. Stay connected despite a no-internet warning.
No automatic-portal promise is made. The purple setup indication is removed;
ordinary touch controls and blue startup/power checks remain.

## Glitter contrast

The Glitter button dims the full dragon silhouette to 10% of its normal palette
and adds white wing sparkles. Peaks remain capped at 204/255 (80%) per channel.
Frame power limiting, zone/pixel calibration, ambient dimming and user brightness
remain in effect, including the 400 mA USB session ceiling. This is a rendering
percentage, not a measured electrical-power guarantee. Preset/editor region
Glitter behaviour is unchanged.

## Clock, sunrise and rotation

Page initialization synchronizes phone time/time-zone rules and reports success.
Without home internet time, reopen the webpage after power loss: there is no
battery-backed RTC. Sunrise retains 37 wing pixels and 27 dark non-wing pixels;
all existing estimated power limits remain, including computer USB at 400 mA.

Rotation is a persisted on/off setting with a 10–86400 second interval and
collection-order or shuffle selection. It uses active membership, including
owned creations and shared favourites. Shuffle excludes the current dragon when
another is available. Sleep and sunrise pause rotation; waking starts a full
interval. Manual selection, touch selection and collection changes restart it.

## Parent-approved online updates

The dragon setup AP provides no internet connection to the phone or PC. For an
offline update, download the signed file on home Wi-Fi/mobile data BEFORE joining
the dragon network; uploading the saved file then needs no internet. The page
shows this guidance and disables direct checks on setup Wi-Fi.

After setup Wi-Fi closes, on home Wi-Fi with internet and a synced clock, parents can choose **Check for
updates**, review the signed release tag, and choose **Install**. No background
checks or unattended installation occur. The file-upload path remains available.

Release is the default channel and uses GitHub's latest non-prerelease release.
Beta requires an explicit parent selection each unlocked session and shows a USB
recovery warning. Beta reads its signed board manifest from the `firmware-beta`
prerelease's assets; the manifest points to an immutable version tag such as
`v0.3.0-beta.1`. Neither channel installs automatically. Firmware rejects beta tags
in the Release channel and non-beta tags in Beta. No stable 0.3.0 is published yet.

The device fetches `dragon-s3.manifest` or `dragon-c3.manifest` for
`sai021/dragon-kingdom`. The signed manifest contains six newline-
terminated fields: `dragon-online-v1`, board, release tag, decimal byte size,
lowercase SHA-256 and hex RSA signature. The signature covers the first five
fields including newlines. Board, size, tag syntax and signature are verified
before preparing the inactive slot. The binary comes from the signed tag's
immutable download path as `dragon-s3.bin` or `dragon-c3.bin`; no user-supplied URL
is accepted. The complete image digest and ESP image checks gate boot selection.

HTTPS uses the pinned SDK's CA bundle and hostname validation. Redirects must
remain HTTPS on GitHub or its two release-asset hosts. TLS verification is never
disabled. The network task owns HTTPS and a four-message queue; the main loop
alone owns sessions and writes at most one 512-byte message per update call.
Network downloads therefore do not block ordinary lighting/touch in the main loop.
Cancellation or expired/replaced parent sessions abort the transfer. Restore,
reset, scans and other firmware operations are blocked while it runs.

Add `--tag TAG` to the signing command below to generate the online `.manifest`
and raw `.bin` beside the offline package. Publish both board assets on that same
GitHub tag only after acceptance. No signed online release has been published in
this implementation session; an old release without assets produces an explicit
unavailable message and retains the current firmware.

## Offline signed updates

Parents download a matching `.dragon.json` package from GitHub on a phone or PC,
then upload it through the webpage while unlocked. The device needs no internet.
The release package includes a board identifier, byte size, SHA-256 digest,
RSA-2048 PKCS#1 v1.5 SHA-256 signature and hex-encoded application image.
The signature binds `dragon-update-v1\nBOARD\nSIZE\nSHA256\n` exactly. The device
verifies this signed manifest and its own board identity before erasing an inactive
slot. Sequential 512-byte chunks are session-bound; duplicate/wrong offsets are
rejected. Inactivity for 30 seconds or expired/replaced parent sessions aborts the
transfer. Full image hashing and ESP-IDF image validation precede boot selection.
An interrupted transfer never selects the incomplete image.

Two 0x180000-byte app slots retain the old app0 offset at 0x10000 and original
NVS at 0x9000/0x5000. OTA metadata occupies the previously unused 0xE000 sector
pair. No eFuses or hardware secure-boot settings are changed. This provides
signed webpage updates, not protection against someone rewriting flash over USB.

Both pinned SDK configurations enable bootloader/application rollback. The
`extern "C" verifyRollbackLater()` override suppresses Arduino's early automatic
confirmation. After 30 seconds, storage, networking initialization and power-budget
checks confirm the image. Undefined initial OTA metadata is seeded and confirmed
only after those checks, so the first update has a fallback. Unhealthy startup
attempts rollback after 60 seconds; reset/crash before confirmation invokes the
bootloader's rollback on the next boot. These checks cannot establish LED/touch
hardware correctness or future endurance.

`tools/sign_update.py sign --key PRIVATE.pem --board s3 --image APP.bin --output
PACKAGE.dragon.json` creates a package (use `c3` for the other target). The current
private signing key is local under ignored `.tools/release-signing/`; back it up
privately before any device distribution. Only the public verification key is
shipped. Builds never generate/replace keys. The keygen action is a deliberate
trust-root replacement for development, not normal release preparation.

## Backup and reset

Version-1 backups carry a checksummed snapshot of the existing library schema,
sunrise rules, rotation and light calibration. Wi-Fi secrets, parent credentials,
sessions, UTC clock values and diagnostics are excluded. This is a fixed-layout,
versioned S3/C3 format; future struct changes require explicit migration.
Import validates checksums, field bounds, membership, and protected All before
staging anything. Backups are not firmware signatures and are not encrypted.

A verified NVS redo journal stages restores and reset. Boot replays it before
networking and removes it only after all records verify. Interrupted restores
retry at next boot; restore failure disables networking for that boot. The UI
reports staging/restart, not completion before the reboot. Keep a pre-restore
backup until a real reboot and saved-content check succeeds.

## USB migration and recovery

See the [illustrated recovery guide](USB-RECOVERY.md). The new single-device GUI
has port selection, an explicit USB-only power acknowledgement, a recovery button. It does not automatically flash on connection. Existing batch
manufacturing tooling is retained separately.

Candidate recovery bundles live in ignored `.tools/recovery-release/`, separate
from the previous manufacturing set. Prepare both targets with the existing
`flash_support.save_release` helper after building, before using recovery.

The CLI also accepts `--esptool PATH` to use a trusted installed standalone
esptool without Arduino CLI. This does not change Windows policy.

The tool verifies ROM identity and the saved bundle's checksums/layout, reads the
original 20 KiB NVS to ignored local storage, writes only bootloader, partition
 table, OTA metadata and app0, then reads NVS again and requires byte-for-byte
agreement before a startup check. It never uses erase-flash. Reading back unchanged
bytes is required physical migration evidence, not yet established by simulations.

## Acceptance gates

Software results are recorded in PROJECT-STATUS.md. Clean Arduino CLI builds remain
blocked by Windows Application Control on this machine; direct pinned compiler
checks are separate evidence. The [24 October S3 migration](HARDWARE-TEST-2026-10-24.md) was completed after
USB-only power confirmation and ROM identity checks. NVS and the saved-library
baseline survived; app0 reached VALID. Actual online installation/rollback, phone
setup and C3 physical acceptance remain pending.

Required physical tests on BOTH boards:

- Confirm current ROM identity and USB-only power before initial migration; retain
  private pre/post NVS reads, check saved dragons/alarms/home Wi-Fi and parent setup.
- On real iPhone and Android: captive portal plus QR/manual fallback, no play login,
  parent API rejection, wrong-password retry, association across different AP/router
  radio channels, handover/address delivery, AP shutdown with a phone still joined,
  later home-network drop, and power-cycle recovery.
- Interrupt uploads and restart the device; confirm previous application and data.
  Try wrong-board, modified-image and invalid-signature packages. Force failure
  before startup validation and verify bootloader rollback and saved records.
- Interrupt restore writes at multiple points; verify redo completion after reboot.
- Check touch/rotation during saves and networking, full-wing sunrise optics,
  deployed supply/current/thermal behavior, range and endurance.

Supplied hardware files remain unchanged and unvalidated as a final design.
