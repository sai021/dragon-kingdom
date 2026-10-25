# Updater 1.1.0: home and direct setup Wi-Fi

The owner requested both modes after 1.0.0 publication. Firmware remains 0.3.1;
this change does not flash a lamp or change its network credentials.

- Home Wi-Fi: check main releases, discover lamps or add a reachable address,
  then perform a deliberate signed update over the shared home network.
- Dragon setup Wi-Fi: download and verify all four packages while on internet,
  then have the parent join Dragon-Kingdom-XXXXXX in the OS Wi-Fi menu and connect
  directly to 192.168.4.1. No home-network configuration is required. The app does
  not automatically change the computer's network.

The offline set contains the signed release contract, S3/C3 ordinary packages
and S3/C3 legacy bridges. It is published to the user's application-data Firmware
folder in one atomic replacement only after all downloads pass verification.
Failed downloads retain the previous complete set. App restart revalidates the
complete cache; missing, altered or partial files fail closed. Offline package
selection makes no internet requests and does not silently use a network fallback.
Preparing a download never writes to a lamp. Backups and parent session handling
are unchanged. A later offline release requires a fresh preparation on internet.

Direct-mode restart verification allows five minutes. Parents may need to rejoin
the lamp network after reboot; if it disappears, they should rejoin home Wi-Fi.
The verification engine also tries the station IP reported before the update,
so routed networks do not depend entirely on multicast/subnet discovery. Device
identity, installed version, validated startup and saved settings still gate success.

Twenty-one tests cover both boards and both formats, offline local-HTTP transfers
with public downloads forbidden, persistent offline reload, altered/missing cache,
interrupted replacement and AP-to-home address fallback, plus existing signature,
cancel, rollback and saved-settings checks. GUI smoke exercises both modes.
Packaged native-platform checks download the real signed current release and all
four packages, reload the saved set with downloads blocked, and verify selection.
These are simulated/device-independent AP checks; no physical AP association or
post-reboot AP handover is claimed. The earlier real S3 beta-3 Wi-Fi bridge result
remains in the 0.3.1 release record; no additional firmware write was needed here.

Manual edition 1.1 retains ten pages. The revised class notice remains one A4
page with the same three QR addresses. Both were rendered and visually inspected;
all three QR codes decoded to their exact targets. Stable public help/manual URLs
remain unchanged. The app's OS certificate/notarization limitations remain stated.

App source/tag target: 58329ce5ee75e17edf84562835daf0b79f550c93.
All three platform jobs passed in CI run 40174359365. The downloaded Windows ZIP
also passed launch and real-download/offline-reload checks on this PC. Each archive
was checked for the correct public key, bundled CA, dependency source/notices and
absence of credentials/private keys. All five uploaded assets byte-matched the
prepared files before updater-v1.1.0 was published with latest=false. Firmware
latest remains v0.3.1. The stable family guide links the new three platform files;
manual edition 1.1 and the updated class notice replace the same public PDF URLs.
