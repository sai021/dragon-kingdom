# Shipped beta-3 fleet and HTTPS remediation - 25 October 2026

The owner confirms that all units have shipped and all shipped units run v0.3.0-beta.3. Board counts/serial inventory were not supplied. This supersedes earlier statements that the dispatched firmware mix was unknown. No customer device was accessed, no customer was contacted, and no feed/release was changed by this review.

## Confirmed failure and available update route

The published beta-3 transport uses a 512-byte HTTP transmit buffer. The later live investigation found GitHub signed redirect request lines around 886 bytes; the HTTP client can fail building that request before sending and present it as a verified-HTTPS connection failure. Beta 6 and later increase the bounded request buffer to 1,152 bytes for a 1,024-byte URL capacity, retaining certificate checks, trusted-host restrictions and signed-image verification. This is not evidence that every possible HTTPS failure has the same cause.

Changing only a server manifest cannot enlarge an already-installed beta-3 client buffer. Shipped lamps therefore cannot be assumed to download this fix themselves. A working local beta-3 webpage nevertheless supports signed file upload over local HTTP, independently of the lamp's outgoing HTTPS client. Parents can download a file with their phone/computer internet connection, then upload it through the lamp's existing parent page over Wi-Fi. No enclosure opening or laptop USB is required for that path. It depends on a reachable local webpage, stable power/Wi-Fi and a working upload; USB service remains fallback rather than the first instruction.

Verified the exact published beta-3 source at 38a53018c230dba5b85b7c3edb1f6bf05917a661. Its browser requires package format 1 and its server verifies the v1 board/size/hash signature. Ordinary beta-9 format-2 files will be rejected by this older webpage. The beta-3 public key matches the current trust root. Both already-published beta-9 legacy bridges have verified format-1 signatures and image hashes under that same key.

## Practical parent workflow, once the shipping target is approved/tested

1. Use phone/computer internet to download the board-matched signed **legacy bridge** package, retaining the .dragon.json file rather than raw .bin. Beta 3 displays ESP32-S3 or ESP32-C3 on its page and under Firmware update after parent unlock.
2. Stay on the same home Wi-Fi as the lamp and open its saved local page. If using the dragon setup network instead, download the file first, then join that network and reopen the page. The upload itself does not need internet.
3. Open **Parent settings**, unlock with the existing parent password, and use **Download backup** first.
4. Under **Firmware update**, choose **Signed firmware package**, select the matching legacy-bridge file, and press **Install firmware**. Keep normal product power and Wi-Fi connected and the page open throughout. Do not connect laptop USB for this Wi-Fi update.
5. After the verified restart, reconnect/reload the page and confirm firmware version, saved dragons/settings, normal lighting and touch. Do not factory-reset or erase saved data as an update step.

This is an internal workflow draft, not a customer message or instruction to deploy beta 9 fleet-wide. Existing bridge downloads are on [the beta-9 release page](https://github.com/sai021/dragon-kingdom/releases/tag/v0.3.0-beta.9), named dragon-s3-legacy-bridge.dragon.json and dragon-c3-legacy-bridge.dragon.json. They install the full beta-9 application, not just the HTTPS change. No HTTPS-only beta-3 patch has been built or released in this review.

## Rollout decision and online feeds

Beta 9 remains a manual-download prerelease with an unresolved test-S3 restart investigation. A targeted shipping hotfix or a limited validated rollout should precede advising every customer to change firmware; do not treat the S3 quiet comparison windows as full acceptance. The existing Release and Beta feeds remain old-format. Installing the beta-9 bridge fixes the transport implementation but does not by itself make those old feeds compatible with its format-2 updater. Coordinated feed migration is separate from the one-time local upload and must preserve an explicit path for beta-3 customers. Do not tell customers that online updates are already restored simply by selecting Beta or changing the device clock.

The next concrete engineering step is to choose a shipping target, test the exact beta-3-to-target legacy upload on both board types under normal product power, verify settings/calibration and HTTP/HTTPS behavior, then publish clear board-specific download links and parent instructions. Any customer outreach or new release/feed mutation requires its own authorization. Certificate verification must remain enabled.
