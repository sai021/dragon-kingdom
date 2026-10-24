# Physical S3 migration — 24 October 2026

This record covers the connected S3 only. It does not establish C3 physical
acceptance, real-phone coverage or a complete internet update/rollback test.

## Safety and identity

The user explicitly confirmed that external/main power was disconnected and the
internal laptop USB connection was the only power source. ROM detection on the
current COM21 identified ESP32-S3 QFN56 revision 0.2, 4 MB embedded flash and 2 MB
PSRAM. The original firmware reported the computer-USB 400 mA estimated ceiling.
No dual-power or external-only test was performed.

## Backup and migration

A monolithic 4 MB read stopped around 1 MB with an esptool serial-stream error.
No flash write had occurred. Sixteen independent 256 KiB reads at 115200 baud
subsequently completed the original full-flash backup. Its SHA-256 is:

`ec77a353e78dc08c38ce8dfd6c3031af02a35fd37b21ac98873928f5e176387c`

The actual original table was checked: NVS 0x9000/0x5000, factory app0
0x10000/0x180000, reserved 0x190000/0x260000 and coredump 0x3F0000/0x10000.
The standalone esptool 4.8.1 was explicitly selected, since Windows Application
Control blocks Arduino CLI. No Windows policy was changed.

The recovery tool rechecked ROM identity, candidate checksums and live NVS layout;
read NVS; wrote only bootloader, partition table, erased OTA metadata and app0;
read NVS again; then reset the verified board and checked serial startup. The NVS
bytes matched before/after, and independently matched the original full backup's
0x9000..0xDFFF slice. No whole-flash erase or NVS write was requested by recovery.

Installed S3 candidate application: 1,364,064 bytes, SHA-256:

`a11955addc44c85db7bc8cb914b022ab489ca02cc0268f30c6e91f10b7aa1cf1`

Original firmware and application data, raw NVS, serial captures, one-use setup
code and recovery session files stay in ignored local output directories. They
are not publication artifacts. No parent password was chosen or stored by the agent.

## Observed runtime

- Library readiness, active All profile, two custom dragons and generation 14
  matched the pre-migration baseline.
- Increasing uptime and the 400 mA computer-USB ceiling passed startup checks.
  No electrical current measurement or deployed-supply test was made.
- After the validation window, serial reported `firmware_validation ready=1`,
  running partition `app0` and `ota_state=2` (VALID).
- The password-protected AP was reported active while saved home Wi-Fi was joining.
  The association failed with reported disconnect reason 210; the cause is not
  established. The attempt stopped and STA was disabled. At roughly 158 seconds
  uptime, the AP remained active and automatic joining remained stopped, with
  credentials still marked configured and the radio setting at 34 quarter-dBm.
- No visual LED, touch, LDR, wing-optics or phone observations were supplied in
  this session. AP driver state is not a phone/range measurement.

## Live webpage/online limits

Windows rejected the laptop WLAN query with missing location permission and an
access/elevation error, so the laptop was not switched to the dragon network.
The saved home network did not connect. Real webpage/HTTPS downloads could not be
verified in this session. The native actual-route and browser simulations remain
software evidence only. A private one-use USB setup code was generated for the
owner to choose a parent password; it expires after ten minutes.

No signed GitHub release assets were published. The online button therefore needs
a published signed manifest and binary before a complete real installation can be
exercised. Wrong-board/signature rejection, interrupted download and session
cancellation passed native tests with deterministic adapters; actual powered
interruption and bootloader rollback are still pending, along with real iPhone/
Android captive setup, channel changes, AP shutdown on a successful join and
cold power-cycle recovery. The C3 has a software-built image but was not connected
or flashed here.


## Follow-up: location permission and live embedded webpage

After the user enabled Windows Location services, `netsh wlan show interfaces`
succeeded without elevation. The laptop temporarily joined the dragon's actual
password-protected AP using the documented AP key. Its previous Wi-Fi profile was
recorded privately and restored in a finally block; the temporary test profile was
removed. This supersedes the WLAN-access blocker above for this PC/session.

Actual ESP32 HTTP results, without parent credentials:

- Root, state, library, dragons, sunrise and rotation GETs returned HTTP 200.
- Sixteen sensitive routes returned HTTP 401: backup, scan, update status, online
  status, Wi-Fi save/retry/forget, restore, reset, upload start/chunk/finish/abort,
  and online check/install/cancel. POSTs included the normal custom request header,
  so these checks exercised the parent boundary rather than only the CSRF guard.
- Headless Edge loaded the real embedded page at a 390x844 viewport, enabled the
  dragon controls and confirmed automatic clock sync. The real alarm endpoint
  reported `clockReady=true`; no JavaScript page errors occurred. Browser timezone
  was Australia/Sydney. No parent password was set and no collection was modified.

Private API results, connection logs and a real-page screenshot remain under the
ignored online-update output directory. This is live device/desktop evidence,
not an iPhone/Android or captive-portal opening test. Saved home Wi-Fi connection,
real internet firmware download/install, successful-join AP shutdown, channel
handover, physical interruption and rollback remain unverified.


## Follow-up: fixed parent password and hidden controls

The user superseded the credential-setup design: parent access now always uses
`dragon123`. No password change, USB code or additional top-level gate is required.
The parent area shows its password form; sensitive controls are hidden/inert until
accepted, and hide on Lock, reload, expiry or rejection. Firmware endpoint session
checks remain independent of the interface. Software tests cover those behaviors.

A real HTTP upload of the first revision was interrupted around 67% with a reset
TCP connection. The local installer aborted best-effort and restored laptop Wi-Fi.
Serial subsequently showed the original app0 still VALID, increasing uptime,
two creations/generation 14 and the 400 mA ceiling. No incomplete image was selected.
The reason for the TCP interruption is not established. Connecting a laptop/phone
to the dragon AP removes internet access through that Wi-Fi network; the page now
explains download-before-joining for offline updates and disables direct checks
until the dragon is on home Wi-Fi and its setup AP has closed.

To keep the laptop online, the final revision was installed through internal USB
under the already confirmed USB-only power arrangement. ROM identity matched the
same S3, the live two-slot table was checked and OTA metadata confirmed valid app0.
Only the application at 0x10000 was written. The 0x8000..0xFFFF range (partition
table, NVS and OTA metadata) matched byte-for-byte before and after the write.
The verified board was reset normally. Serial confirmed updated app0 VALID with
`firmware_validation ready=1`, two creations/generation 14 intact and the 400 mA
computer-USB ceiling retained. No whole-flash erase was used.

Final S3 image: 1,363,808 bytes, SHA-256:

`4908c7da8f9dadc142bd3ab569723b44b38aa81e1c11f44399e23e3b52d080fc`

C3 software image: 1,406,752 bytes; not physically flashed. Both use the pinned
cached-dependency compiler/link workflow; clean Arduino CLI builds remain blocked.
The fixed-parent browser simulations pass, including offline-only direct-update
button behavior, wrong passwords, lock, reload and expiry. Actual live HTTP checks
above apply to the preceding candidate; the new hidden-settings/password interface
still needs owner phone confirmation. Online download/install and physical rollback
remain open gates. Earlier one-use setup instructions are obsolete and have been
replaced locally with the fixed-password instructions.
