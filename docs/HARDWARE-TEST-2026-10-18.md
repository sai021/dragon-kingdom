# Physical S3 development session — 18 October 2026

## Setup and evidence boundaries

The user connected the assembled prototype by laptop USB and explicitly
confirmed external/main power was disconnected. ROM identity confirmed an
ESP32-S3 with 4 MB flash and 2 MB PSRAM on COM17. This is S3 evidence; no C3
was physically tested. The original NVS area was backed up locally before
upload. Raw serial captures, network details, NVS images and upload logs are
kept under ignored `dragon-firmware/.tools/live-hardware-20261018/`.

## Passed on real hardware

- The sunrise firmware uploaded successfully and ran with increasing uptime,
  ready library and no observed panic during the recorded test windows.
- Startup reported `computer_usb_cap=1` and a 400 mA estimated session ceiling.
  Startup ADC samples were approximately 5.03–5.09 V. These are divider-derived
  readings, not independent meter measurements. Runtime voltage sampling stays
  stopped, as designed.
- The user confirmed the visible orange → blue → glitter → off → Blue sequence.
  Serial state matched each requested mode and the reported estimates stayed
  below the USB ceiling.
- The user covered the LDR for about ten seconds, then uncovered it. Recorded
  raw readings ranged from 1,556 to 2,652; ambient gain ranged from 50% to 70%.
  Existing saved calibration was retained.
- The user confirmed a physical tap advanced the dragon. Serial reported a
  press count of one and selection of Sundew.
- The real 30-second sunrise preview reported 0%, 25%, 52%, 78% and 100%, then
  stopped after its hold and returned to normal. The highest reported current
  estimate in that capture was 350 mA; uptime did not reverse. This confirms
  the device state machine. On a replay, the user confirmed the wings gradually
  brightened and then returned to normal. Precise optical region isolation was
  not independently measured.
- The batch startup verifier passed after enabling native USB CDC DTR while
  keeping RTS inactive. This fixes the observed silent status capture with
  DTR disabled.

## Network investigation

The supplied home network was detected on 2.4 GHz at approximately -60 dBm
for its strongest access point, with WPA2 security. Joining did not complete;
the board reported disconnect reasons 4 (disassociation due to inactivity)
and 15 (four-way handshake timeout). The user confirmed the supplied password
and reported recent network instability, offering an alternate test network.
This does not establish a firmware fault or an incorrect password.

USB diagnostics now expose connection status, pending-join state, disconnect
reason and asynchronous scan results. Credential input uses bounded hex framing;
responses do not echo passwords. Home credentials still save only after a
successful connection, using the existing browser provisioning path. The trusted
USB setup helper takes a hidden password prompt or an ignored local JSON file.

The phone hotspot supplied an IP address to the board, but this computer could
not resolve its local ARP address. Peer isolation is suspected, not established.
The user enabled Pixel USB tethering for computer internet and joined the
dragon's setup Wi-Fi directly. Real authenticated HTTP and headless Edge then
loaded the embedded page at `192.168.4.1`; the phone-clock sync completed,
brightness changed to 40% and was restored to 100%, with no page errors.
A mobile-width screenshot was inspected separately from simulated UI tests.

A join-state bug was found: the radio could connect after the old 20-second
deadline while pending credentials had already been discarded. The deadline
is now 60 seconds and a late connection saves credentials only if its SSID
matches the pending request. Native regression tests cover both matching and
mismatching cases. A stricter cancellation experiment stalled on hardware;
it was reverted and the recovery build uploaded and passed startup checks.
A subsequent reset reported configured=1, confirming the pending network
credentials had eventually saved. The phone hotspot still failed to sustain
a usable connection; disconnect reasons 2 and 15 were observed. Normal boot
therefore hid setup Wi-Fi, as designed for a configured device.

Added and physically exercised trusted USB recovery: `wifi setup` reopened
the access point without erasing home credentials, and `alarm disable`
saved disabled state and stopped the current sunrise. The new upload passed
the increasing-uptime, ready-library and 400 mA startup verifier.

A real daily alarm was saved for two minutes ahead with a one-minute rise.
HTTP reported an automatic, non-preview start and increasing progress through
5%, 22%, 46%, 70%, 90% and 99%. Following a Wi-Fi channel interruption, USB
confirmed 100% progress and successfully stopped the occurrence. The temporary
alarm was subsequently saved disabled over USB. This is
real scheduling evidence, separate from the user-confirmed preview.

Final recovery builds: S3 app 1,147,250 bytes/static RAM 51,300 bytes; C3 app
1,171,166 bytes/static RAM 42,256 bytes. Both fit the 1,572,864-byte app
partition. Separate saved flasher bundles were refreshed and checksum-verified.
All 23 Python tests and 13 native suites passed.

## Router follow-up

The user supplied a separate router network and then corrected its case-sensitive
SSID. The corrected router was physically scanned on channel 11 at about
-58 dBm, advertising mixed WPA/WPA2 authentication. Credentials remain in
ignored local files. A station restart before changing configuration restored
working scans, but joining still exposed a separate firmware timing defect.

The loop sampled `now` before serial commands, and the web update used that
sample after handling HTTP requests. Commands could set `started` or
`apActivity` to a later millisecond; unsigned subtraction then looked like a
49-day timeout, immediately cancelling a new join or closing a reopened AP.
The loop now refreshes time after commands/network handling; the network
handler refreshes after requests and before AP timeout checks. Short-deadline
policy also rejects future timestamps. Regression cases cover a newly started
join and a freshly reopened AP alongside genuine timer rollover.

The S3 timing-fix upload passed startup verification. A fresh join remained
`joining=1` after acceptance, correcting the previous immediate cancellation,
but the corrected router join was still not confirmed at that stage. Both
S3/C3 builds and saved bundle checksums passed; 23 Python tests and 13 native
suites passed, including the future-timestamp regression cases.

The user changed the Slate Plus (GL-A1300) router to WPA2-PSK. A new
production-firmware attempt still failed to obtain an IP address. Runtime
modem sleep was disabled temporarily for comparison without a confirmed join.
An ignored Wi-Fi-only diagnostic then used the same S3 target, pinned Arduino
core and NETWORK_EVENTS_MUTEX, cleared the 64 matrix LEDs, disabled modem
sleep, and tried the corrected credentials without Dragon web/rendering code.
It also reported disconnect reasons 7 and 4 and no IP during its capture.
This reproduces the failure outside the Dragon application; it does not
distinguish board/RF, Wi-Fi-library and router causes. The user then moved the router to about 0.5�1 metre from the ESP32.
The production-firmware retry still reported no IP and disconnect reason 4;
no successful close-range connection was confirmed at that stage. Router-side
logs were inspected next. Credentials and diagnostic sources/binaries remain
in ignored local output. Full Dragon firmware was restored successfully, then passed the USB
startup verifier with increasing uptime, ready library and the 400 mA
estimated ceiling. USB confirmed the alarm remains disabled and reopened
setup Wi-Fi.

## Successful router connection at lower transmit power

The user signed into the Slate Plus admin interface. Read-only inspection
confirmed the corrected 2.4 GHz SSID, WPA2-PSK, channel 11, 11g/n mode,
20/40 MHz bandwidth and low router TX setting. No router settings were changed
by the agent. Hostapd repeatedly reported that the ESP32 did not acknowledge
an authentication response, preceding the WPA password handshake.

The Wi-Fi-only diagnostic was repeated at 8.5 dBm ESP32 transmit power
(34 quarter-dBm units). With the router at close range and matrix LEDs off,
it connected with RSSI about -24 dBm and obtained a DHCP address. Router logs
independently confirmed DHCPREQUEST/DHCPACK for the same device. This is an
observed radio-setting comparison, not proof of a power-supply or antenna fault.

The full Dragon firmware now reapplies the 8.5 dBm limit when starting a station
connection. It connected with its normal modem-sleep configuration and saved
the new router credentials. Real authenticated HTTP loaded the embedded page,
state, library and alarm APIs through the router. Brightness changed to 40%
and was restored to 100%. This router check used HTTP/API requests; the earlier
mobile-width Edge rendering check was over direct setup Wi-Fi.

A temporary profile (40% glow, two favourites) and custom dragon were saved.
All-profile deletion correctly returned 403. After a hardware reset through
the serial loader, the full firmware automatically rejoined the router and
HTTP verified the profile, custom colours/name and disabled alarm persisted.
The temporary objects were deleted and the original All/Blue/100% lighting
restored. The original 07:00, 20-minute alarm settings were restored, disabled.
A final startup verification passed with the estimated 400 mA USB ceiling.
Both S3/C3 saved flasher bundles were refreshed and checksum-verified. The
23 Python tests and 13 native suites passed. C3 remains physically untested.

## Two-metre and house-network follow-up

The user moved the Slate Plus to approximately 2 metres; this is a short-range
check, not its normal household placement. A two-minute monitor spanning the
move completed 24 authenticated HTTP state checks with zero failures. RSSI
changed from about -24/-25 dBm close-up to -58 through -62 dBm at the weaker
position. A serial-loader hardware reset then automatically reconnected and
served HTTP again after approximately 9.4 seconds. Startup still passed the
ready-library, increasing-uptime and estimated 400 mA USB checks.

The subsequent switch to the original house network produced a crash report
from the provisioning helper; its original stack trace was not captured. A
fresh serial check showed reset uptime. A logged retry connected and saved
the house network at about -58 dBm, and authenticated HTTP confirmed it was
reachable through the current computer route. The responder had remained alive
while the station interface was destroyed/recreated during a network switch.
The connection path now stops mDNS before destroying/recreating STA and removes
redundant early disconnect calls. Four logged switches (house to Slate, Slate
to house, repeated) each saved the requested network and passed authenticated
HTTP checks. No panic or uptime reversal was captured across those switches.
The original crash cause remains unproven without its stack trace; the new
teardown order addresses an identified lifecycle hazard. Final house-network
restart check then rejoined the saved house network and served HTTP in about
9.1 seconds. Ten further HTTP samples over 30 seconds and a brightness change/
restore passed. The final startup verifier confirmed increasing uptime, ready
library and the estimated 400 mA USB ceiling; the alarm remained disabled.
The board was left connected to the house network. Both final S3/C3 flasher
bundles were refreshed and checksum-verified; 23 Python and 13 native suites
passed. These short checks do not establish long-term reliability.

## Outstanding

- Independent optical region isolation and internet/NTP clock recovery after a full power cut.
- Broader room/house coverage, final enclosed placement and longer connection/reconnection reliability.
- Full power-cycle, long-duration reliability and independent voltage/current
  measurements. Laptop USB testing cannot validate the deployed external supply.
- C3 physical compatibility/startup/ADC/radio tests and final mechanical/PCB fit.
