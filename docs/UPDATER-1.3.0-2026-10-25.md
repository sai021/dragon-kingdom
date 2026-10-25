# Easy Update 1.3.0

The owner requested Easy Update branding, offline mode selected at launch,
a prefilled parent password and installation without another confirmation click.
The app and executable/bundle are named Dragon Kingdom Easy Update. Stable ZIP
asset filenames remain unchanged for existing release tooling. The bundle ID
stays stable for OS permission identity.

Parent password dragon123 is prefilled in an editable masked field. An intentional
edit is preserved across mode changes and successful updates for subsequent lamps.
Neither default nor edited passwords are persisted to disk. Update selected dragon
is the explicit installation action; the old extra confirmation dialog is removed.
Connecting to an AP still never installs firmware. Signature, backup, version,
board, direct-mode home-connection refusal and reboot/settings checks are unchanged.
The close-after-failed-Wi-Fi-restoration prompt is retained.

Offline/direct mode is the initial selection. The app prepares signed files while
internet is available before scanning or joining. Home Wi-Fi is an alternative for
already configured lamps: firmware closes AP 15 seconds after joining home Wi-Fi.
Making Easy Update the recommended method does not remove that old-firmware limit.

## Validation and publication

Source/tag target: 7162dd16253efcd61d886cad078d38e123830548.
CI run: https://github.com/sai021/dragon-kingdom/actions/runs/40189391430
Thirty-three tests include default mode/password, editable password preservation,
one-click installation with default and edited credentials, plus existing simulated
HTTP lamp, signature, offline cache, reconnect and native API checks.

The user manual edition 1.3 is ten pages and recommends Easy Update first. The
class notice is one A4 page. All manual pages and the class notice were rendered
and visually checked. The three QR destinations decode unchanged: /update/,
/setup/ and local http://192.168.4.1/. Public help URLs remain stable.

No physical firmware write or new radio association test is part of this UI change.
Earlier physical Windows association/read/return evidence remains separate from
simulation and package smoke checks. Mac association and post-reboot radio
handover remain physically unverified. Firmware stays at 0.3.1; updater releases
must remain non-latest. Windows is unsigned; Mac bundles use ad-hoc signing and
are not Apple notarized. Manual connection and phone-only alternatives remain.

All three package jobs passed. Downloaded Windows ZIP self-test and real signed
HTTPS/offline reload checks passed on this PC. All three archives contain the
correct public key, CA bundle and dependency notices/source; both built Mac plists
have the new executable name, version 1.3.0 and required permission descriptions.
All five uploaded assets were downloaded and byte-compared before publication.
The updater-v1.3.0 release is public with latest=false; GitHub latest remains v0.3.1.
Family guide, setup page, manual and notice were pushed to gh-pages at 45d7d9a.
Unauthenticated public downloads match all three archive hashes; live manual and
notice match local PDF bytes, and the live guide shows all three 1.3.0 buttons.
