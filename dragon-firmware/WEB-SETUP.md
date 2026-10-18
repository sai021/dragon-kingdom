# Dragon Kingdom connection prototype

The interface includes on-device phone controls, Wi-Fi setup, profiles and
custom dragon storage. See PROFILES-AND-CREATIONS.md for the editor and favourites.
Weather and printed QR cards are subsequent milestones.

## Connecting

The phone page also includes **Sunrise alarm**: choose a daily wake-up time and
a 1-120 minute sunrise, then Save. Wings and wing edges warm from orange to
bright sunrise light, including while sleeping; power limits still apply.
Preview takes 30 seconds. Stop/touch/play dismisses the current sunrise; disable
the checkbox and Save to turn off the daily schedule. The normal sunrise holds
for 30 minutes before returning to prior lighting. The alarm has no sound.

Saving synchronizes the device from the phone and persists its timezone rules,
including the next 400 days of DST transitions. Opening the page also syncs in
RAM. After a power cut the device needs internet time through home Wi-Fi or
the page opened again; until then it waits rather than guessing the time.
The UI reports when the clock needs setting and retries initial load failures.
Save remains unavailable until the existing alarm fields load. Clock sync can
also recover those fields; polling preserves later edits. Save the alarm at least
once a year, and after changing time zone, to refresh its persisted rules. The schedule survives restart in
its own checksummed NVS record; library and home Wi-Fi data are unchanged.

On first use, the dragon creates `Dragon-Kingdom-XXXXXX`. The shared setup password is
`dragon123`; browser login is `parent` with that same password. This firmware
also replaces older random device-access passwords on first boot after updating,
without changing saved home Wi-Fi settings, profiles or creations. Older setup
cards need their password updated. This is a convenience password: anyone who
knows it and can reach the device can change its settings.
The developer can capture the `Dragon web:` serial line at 115200 baud and
put the network name and password on the family's setup card before handover.
Parents should never need a serial monitor or coding tools.

`tools/capture_web_setup.py --port YOUR_PORT` captures the boot line and generates
`.tools/dragon-setup-card.html`, plus local credential data. Start capture
immediately after uploading or resetting the board. Use the currently detected
port rather than one copied from a previous log. These files contain the
setup password and are intentionally kept in the ignored `.tools` directory.
The capture log redacts the password.

Join this network and open `http://192.168.4.1/`. Captive portal redirection is
provided, but manually opening that address is the reliable fallback. Choose
to stay on the network if the phone warns that it has no internet. The browser
login is `parent`, with the same password as the dragon network.

The page provides 79 selectable supplied dragons in 81 stable storage slots,
plus saved creations, glitter, fire, breathing, rainbow, return to normal
dragon animation, sleep/wake and brightness. Effects persist until changed.
Touch and web use the same lighting state. The page refreshes every 3 seconds.
Wait for a control or save to finish before tapping the next action. Conflicting controls
are disabled while a command is pending, with a waiting message. Empty profiles
keep play controls disabled until favourites or a creation are added. Failed
saves keep their draft; stale collection forms ask for a reload before saving.
Note unsaved choices before reloading, because a reload discards the draft.

Open **For grown-ups · Wi-Fi & help**, tap **Find my Wi-Fi**, then choose a name
from the name field's suggestions. The search runs asynchronously so it does
not wait in the animation loop. Hidden networks can be entered manually.
The password has an optional show/hide control. Wi-Fi searching and connection
attempts cannot run concurrently.

Enter the home network name and password. Credentials are committed as one
record only after the ESP32 successfully joins Wi-Fi. A failed replacement
leaves previously saved credentials intact. Connection to Wi-Fi does not
establish whether the network has internet access.

Once connected, the page prominently displays a full, bookmarkable `.local` URL
and numeric fallback above the play controls. The links remain visible in the
current tab if the setup connection drops. The unique name (for example,
`http://Dragon-Kingdom-a1b2c3.local/`) uses mDNS and stays the same when the router
changes the numeric address. Local discovery must be supported by the phone
and network; no router configuration is required.
Rejoin home Wi-Fi and open one of those addresses. Guest networks that isolate
devices can prevent both numeric HTTP and .local discovery; the direct dragon
network still works. Use a home network that allows local device communication.
The device supports 2.4 GHz Wi-Fi. Home passwords never appear in status or logs.

## Reopening setup

Hold the touch pad while plugging in and keep holding through the five blue
startup pulses. The first sensor sample is taken after 500 ms, then a continuous
two-second hold is required. Release when the short purple indication appears
after the power test. The setup hold is consumed so it cannot dim the dragon.
Existing credentials are retained. This gesture currently supports TTP223 only.

An unconfigured device leaves its access point available indefinitely. A
configured device closes it after five minutes without clients or authenticated
requests. Losing home Wi-Fi does not open the access point automatically:
ordinary dragon play continues and connection is retried once per minute.

The parent area's **Forget home Wi-Fi** control asks for confirmation, opens
the setup access point, then removes the saved home network. It preserves the
device's setup password and dragon catalog. Rejoin the dragon network using
the setup card to continue. If setup Wi-Fi cannot open, saved credentials stay.

The page highlights the active effect and changes Sleep/Wake to match device
state. Reconnection addresses remain available in the browser tab if the
setup connection drops. Parent settings are collapsed below the play controls.

## Editing and automated checks

Edit `web/dragon-kingdom.html`; `tools/dev.py` regenerates `DragonWebPage.h` before
each build. Do not edit the generated header. The page has no external scripts,
fonts or images and works without an internet connection.

`tests/test_connection.cpp` checks the shared boot/recovery policy, idle timeout,
touch hold and timer rollover. The native lighting tests exclude the radio
adapter and still exercise the actual renderer and touch code.

`tools/test_web.cjs` checks the phone interface in a headless browser against
simulated device responses. Pass the Playwright package location and, optionally,
the browser executable as arguments. These checks do not replace testing the
actual ESP32 Wi-Fi stack or testing on an iPhone/Android phone.

## Prototype validation and limits

Networking starts only when the startup ceiling can cover the controller,
radio allowance and panel idle draw. At the 300 mA fallback, Wi-Fi stays off and
touch lighting continues. At higher passing levels, rendering reserves an
extra provisional 50 mA for Wi-Fi by reducing the LED budget. This is an estimate,
not a measured Wi-Fi peak allowance; verify real supply behaviour before handing
the prototype to children. A failed power sweep retains its diagnostic pattern.

The interface is local HTTP with browser authentication, protected Wi-Fi setup,
and a required custom header on mutations to reject ordinary cross-site forms.
HTTP is not encrypted on the home network. This is a local prototype, with no
internet exposure, remote control, cloud accounts or OTA update endpoint.

Hardware/phone acceptance checks still required:

- First boot: AP available, login accepted, controls respond on iPhone and Android.
- Touch held at power-on: setup opens; release causes no ordinary touch action.
- Normal touch: tap/double tap/hold continue to work during web requests.
- Wrong password: useful error, no loss of saved working network.
- Correct password: address shown, home-network control works after reconnecting.
- Unplug/replug: credentials retained, normal boot does not open AP.
- Router outage: play continues, no new AP, reconnection recovers.
- Configured setup: AP closes after inactivity, remains while a phone is joined.
- Wi-Fi traffic: voltage and animation stable on the intended charger/cable.
- For multiple prepared units: unique network names and addresses; the access
  password is deliberately shared, not unique per device.
- Existing power diagnostics, ambient dimming and USB cap remain effective.

Build with `tools/dev.py build`; upload only after preparing a setup card and
being ready to perform these checks. Factory reset and credential recovery by
parents need a designed flow before family release.

Keep `DragonPrototype/build_opt.h` in the sketch. It enables the Arduino
network event callback mutex for every compiled translation unit. The first
hardware upload exposed a callback-dispatch startup crash; enabling this
locking eliminated the reproduced crash in the laptop-powered startup check.
