# Corrected C3 parent-page review - 25 October 2026

Inspected the real C3 webpage in the in-app browser after its beta-4 bridge update. This was a live browser inspection, not the simulated phone suite. The browser viewport was approximately 556 pixels wide; actual iPhone/Android coverage remains pending.

## Resolution

These findings were addressed in beta 6 and checked on the corrected C3. See [implementation, test results and physical evidence](PARENT-PAGE-FIXES-2026-10-25.md). The observations below record the earlier beta-4 page.

## Working

- The page reports beta 4 and ESP32-C3, home Wi-Fi connected, with hostname and numeric-address guidance.
- Ordinary play is available without unlocking Parent settings.
- Parent settings unlock with the existing parent password; the login form disappears, the password field is cleared, and protected controls become visible.
- Board guidance selects the C3 package. Release is the default channel, and no installable online release was displayed during inspection.
- Lock parent settings hides the protected controls and restores the login form. The session was left locked.

## Findings

1. **Online checking currently fails.** The live update status is "Could not establish verified HTTPS. Check internet and the clock." Clicking Check for updates reproduced that result. This is the transport-open failure path, before manifest compatibility parsing. The current diagnostic does not distinguish DNS, socket, TLS certificate or clock failures; the root cause is not established. Do not weaken certificate verification to work around it.
2. **Return to Release has an oversized checkbox.** Its label-wrapped input inherits the general full-width, padded, 52-pixel-minimum input styling instead of the existing `.check` treatment. It appears as a large square on a separate row. The rotation checkbox uses the same uncorrected markup pattern, identified from source; it was not toggled on the live unit.
3. **Wi-Fi handover wording is stale.** The device reports accessPoint=false and the page is already being used on home Wi-Fi, but the connection status still says "Setup Wi-Fi closes shortly; join home Wi-Fi and open the address above." This should describe the current completed connection rather than a handover that has finished.
4. **Action and section spacing is cramped.** The support and backup buttons meet with no gap; the restore button is immediately followed by the Firmware update heading. Grouping and vertical spacing would make the parent page easier to scan.
5. **Offline upload guidance assumes setup Wi-Fi.** It tells an already-connected home-Wi-Fi user to rejoin the dragon network. A downloaded file can also be uploaded through the existing home-network page; the instructions should make both paths clear.

No firmware was installed by this review, and no network credentials, saved settings, restore or reset controls were changed. Opening the webpage performs its normal phone-clock synchronization. Update checking was the only deliberate device action besides parent login/logout. Private household details are omitted from this review.

Next implementation should fix the checkbox and parent-page presentation, add browser assertions for actual checkbox geometry and current connection wording, and add precise bounded transport diagnostics before investigating the HTTPS failure on the device. Preserve the accepted beta-4 image and existing signed bundle as immutable evidence; any revised firmware requires a new candidate identity and its own tests.
