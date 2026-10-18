# Low-power matrix tester

Standalone sketch for the documented Dragon Kingdom circuit: ESP32-S3 SuperMini,
GPIO12 through the existing 330–470 ohm series resistor to DIN of a 64-pixel
WS2812 RGB LED matrix, shared GND and 5V. Verify the built PCB matches this.
Onboard RGB GPIO48 is confirmed by the user's supplied SuperMini product
pinout (18 October 2026); physical LED operation still requires observation.
TTP223 touch on GPIO11 is used (3.3V, active-high momentary mode).
LDR and voltage sensing are not read. No Wi-Fi, Bluetooth initialization,
saved-data access or full-load test. Upload replaces the current application.

## Connection and safety

- Before first attachment, perform the unpowered multimeter checks in
  ../BoardTester/README.md. In particular check 5V/GND shorts and polarity.
- Use laptop USB into the ESP32 only; external/main power stays disconnected.
  The matrix receives the shared USB-derived 5V rail, NOT a GPIO or 3.3V pin.
- A removable matrix connector is supported. Powered hot-swapping is NOT made
  safe by this program. Without a separate matrix power switch, unplug USB
  before swapping. To leave the ESP32 running, pause using touch (amber LED,
  data held LOW), switch the matrix 5V OFF, allow its capacitor to discharge,
  swap, switch matrix 5V ON, then tap/release touch to restart. Keep common GND.
  Confirm the switch isolates ALL matrix power feeds. Amber alone is NOT safe
  to swap: the pause command does not physically disconnect matrix power.
- If powered swapping is required, first design a suitable switched/current-
  limited supply and data isolation/sequencing arrangement. Software cannot
  protect the ESP32/USB source from a wiring short or capacitor inrush.

## Operation

On power-on the onboard LED shows red, green and blue for 0.6 seconds each,
then amber (matrix stays dark). Status brightness is 24/12 for amber and
32 for blue, increased from the original very dim 4/2 and 4 settings.
Starts paused/dark with onboard amber. Release touch after power-on, then tap
and release to start. Each subsequent tap/release alternates running and paused.
A sensor held at boot does not start the test. Holding touch does not repeat.
Every start restarts at red after a 300ms settling delay.
While running, ALL 64 pixels light together at 8/255 on ONE channel.
Red, green and blue each last one second; the three-second cycle repeats.
No white/full-brightness pattern is used. This checks each colour at every
position visually, rather than checking physical pixel address order.
The conservative estimate is about 310mA: 200mA controller + 64mA panel idle +
40.2mA light + 5mA status allowance. A compile-time assertion keeps that model
within the project's 400mA USB ceiling. Actual current remains unmeasured.

Watch that all 64 positions light with the correct colour on every pass, with
no flicker or missing downstream pixels. A failed first pixel/data connection
can stop the rest of the chain. This is a visual test; there is no automatic
green pass because the matrix provides no feedback.

Onboard blue = running; amber = paused. Serial at 115200: `x` clears/pauses,
`r` restarts. No serial connection is necessary: touch controls the test.

This keeps commanded LIGHT output very low, but does not measure or guarantee
current. All 64 pixel controllers still consume idle power, plus the ESP32.
It does not validate full brightness, supply capacity, sensors or other PCB
connections. An attached matrix can retain a prior pattern until cleared.

## Build/upload

Use Arduino-ESP32 3.2.1 and Adafruit NeoPixel 1.12.5, ESP32S3 Dev Module,
USB CDC on boot enabled, 4MB flash. Default partitions are sufficient.
From dragon-firmware:

```powershell
.\.tools\arduino-cli\arduino-cli.exe compile --fqbn 'esp32:esp32:esp32s3:USBMode=hwcdc,CDCOnBoot=cdc,FlashSize=4M' --build-path build/matrix-tester MatrixTester
.\.tools\arduino-cli\arduino-cli.exe board list
.\.tools\arduino-cli\arduino-cli.exe upload --fqbn 'esp32:esp32:esp32s3:USBMode=hwcdc,CDCOnBoot=cdc,FlashSize=4M' --port YOUR_PORT --input-dir build/matrix-tester MatrixTester
```

Use the actually detected port, close serial monitors before upload, and flash
the ESP32 by itself first. Unplug before attaching the PCB/matrix. Physical
verification remains outstanding until run on the actual assembly.
