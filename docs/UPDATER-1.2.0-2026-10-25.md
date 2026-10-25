# Updater 1.2.0: automatic dragon Wi-Fi connection

The owner requested scanning nearby dragon APs and connecting without manually
switching the computer's Wi-Fi for each lamp. Firmware remains 0.3.1; this release
changes only the desktop updater and instructions.

In direct mode, Find dragon Wi-Fi prepares the signed offline set if needed and
lists nearby encrypted Dragon-Kingdom-XXXXXX networks. A parent selects one and
Connect to selected dragon switches Wi-Fi, then checks the HTTP lamp hostname
matches the chosen SSID. Connecting never installs firmware. The existing parent
password, version review and explicit Update selected dragon click remain required.
The app attempts reconnection after reboot and restoration of the original
computer network after update/failure, mode change, explicit return or close.
If restoration fails, the user can close the app and reconnect manually.

Windows uses the Native Wi-Fi API and an in-memory temporary WPA2/AES profile;
it does not save/overwrite user profiles or read home passwords. Mac uses public
CoreWLAN APIs through pinned PyObjC, requests CoreLocation authorization on the
GUI thread and asks the OS to restore the original network without extracting
keychain secrets. Original SSID/profile data remains in RAM. Location/Wi-Fi
permission or managed-device policy can block these APIs; no privacy policy or
security setting is changed by the app. Manual connection remains available.
Mac restoration is best effort and may require manual reconnection.

## Corrected AP restriction

Published beta 3 and current firmware call openAP() at startup, but
ConnectionPolicy closes AP 15 seconds after a successful saved-home join,
regardless of attached clients. Earlier direct-mode instructions omitted this
restriction. The app now refuses direct-mode writes if the lamp reports home
Wi-Fi connected, before login/backup/START. Use Home Wi-Fi mode for those lamps.
Direct mode is for unconfigured lamps or lamps unable to join saved home Wi-Fi;
a power cycle alone does not keep AP open while the saved home network is available.
The guide, manual and class notice now state the restriction.

## Evidence

Thirty-one tests pass, covering session join/return, sequential selection of two
APs, reboot reconnect, AP disappearance, failed join, rejection of foreign SSIDs,
WPA2 profile construction, OS bindings/ABI and refusal of home-connected direct
writes, plus existing signature/backup/offline/rollback/cancellation cases.

A real Windows native scan found two Dragon APs. A controlled test joined one,
read an ESP32-S3 running v0.3.0-beta.3 at 192.168.4.1, matched its hostname to the
selected SSID and confirmed return to the original Wi-Fi. It took about seven
seconds. No firmware or saved lamp settings were written, no power arrangement
was changed and no home password was read. Raw evidence is in ignored .tools
storage; original home-network names/profile details were not logged.

All three platform jobs pass in CI run 40178822064: Windows x64, Apple Silicon
Mac and Intel Mac. Packaged checks exercise both GUI modes, native API bindings,
signed public downloads and offline reload/selection of all four package types.
Mac Wi-Fi association and post-reboot radio handover were not physically tested;
the real Windows test covers association/read/return, not a firmware transfer.
Firmware transfer evidence from the earlier S3 update remains separate.

Manual edition 1.2 remains ten pages; the class notice remains one A4 page. All
final pages were rendered and visually inspected and all three notice QR targets
decoded unchanged. Existing public QR/help addresses are retained.

App source/tag target: 9aad11e78a14d37d99779b8941cda58c8cff00d0.
All three platform archives passed content checks for the correct public key,
bundled CA and dependency notices/source. Mac bundle version and network/location
usage descriptions were checked in the built Info.plist. The downloaded Windows
archive passed native-bindings/GUI launch and signed-download/offline-reload checks
on this PC. All five uploaded assets matched prepared bytes before publication.
The updater-v1.2.0 release was published with latest=false; GitHub latest was
checked afterwards and remains firmware v0.3.1. Public guide/PDF URLs are unchanged.
