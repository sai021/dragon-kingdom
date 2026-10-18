# PCB assembly tester

Separate sketch for the documented ESP32-S3 SuperMini circuit. The actual newly
built PCB has NOT been inspected. Verify pin assignments before use: LDR GPIO9,
100k/20k supply divider GPIO10, active-high momentary TTP223 GPIO11 at 3.3 V,
64-pixel WS2812 matrix GPIO12, onboard addressable RGB GPIO48 (revision-dependent).
Do not use on a different circuit without correcting these constants.

## Minimum multimeter checks — EVERY board, before attaching the ESP32

1. Disconnect USB, external supply and ESP32. Discharge the bulk capacitor
   through a suitable resistor; confirm approximately 0 V in DC voltage mode.
   Never use resistance/continuity mode on a powered board.
2. Inspect solder bridges, capacitor polarity and connector orientation.
3. In resistance mode, measure 5V-to-GND, 3V3-to-GND and 5V-to-3V3 at the ESP32
   connector. Capacitors may initially read low and then rise. Persistent
   near-zero resistance (similar to touching the probes together) is a STOP.
   A continuity beep alone is not a reliable pass/fail with electronics fitted;
   unexplained steady low resistance needs investigation before power.
4. Verify PCB ground to matrix GND and touch GND: near probe resistance.
   Verify PCB 5V to matrix +5V, and PCB 3V3 to touch VCC. Confirm these arrive
   at the correct ESP32 connector positions, viewed in the actual mating orientation.
5. Check GPIO9, GPIO10, GPIO11 and GPIO12 have no direct short to 5V.
   GPIO10 must connect through the 100k upper resistor, not directly to 5V.
   Check the divider parts are 100k from 5V to junction and 20k from junction
   to GND (in-circuit measurements can be affected by parallel paths).

These are screening checks, not proof of all wiring. A direct 5V/GND short can
damage the ESP32 or USB source before firmware starts. Software cannot disconnect
the supply, and a red LED does not make a powered faulty board safe. Unplug it.
For stronger protection use a properly current-limited supply/test fixture.
Never connect laptop USB and external/main power simultaneously.

## Flash and run

Flash the ESP32 by itself first. Arduino IDE: ESP32S3 Dev Module, USB CDC on boot
enabled, 4MB flash, library Adafruit NeoPixel 1.12.5, Arduino-ESP32 3.2.1.
This sketch uses the default partition scheme, not the product custom partitions.
Uploading replaces its running application; the tester does not read or erase
product profiles/settings. Restore product firmware afterwards as needed.

CLI, from dragon-firmware (use the actual current port from board list):

```powershell
.\.tools\arduino-cli\arduino-cli.exe compile --fqbn 'esp32:esp32:esp32s3:USBMode=hwcdc,CDCOnBoot=cdc,FlashSize=4M' --build-path build/board-tester BoardTester
.\.tools\arduino-cli\arduino-cli.exe board list
.\.tools\arduino-cli\arduino-cli.exe upload --fqbn 'esp32:esp32:esp32s3:USBMode=hwcdc,CDCOnBoot=cdc,FlashSize=4M' --port YOUR_PORT --input-dir build/board-tester BoardTester
```

1. Verify the ESP32 alone shows yellow onboard. If not, verify the onboard RGB
   pin/type before relying on its colour. Unplug it.
2. Complete the checks above. Connect the PCB with matrix and touch fitted using
   secure removable connections. Keep external power disconnected.
3. Power from ESP32 USB only. Open serial at 115200 baud. Send lowercase `g`.
4. Cover then uncover/illuminate the LDR in its 20-second window. The raw ADC
   range must change by at least 400 counts; this checks response, not calibration.
5. Release touch for one second, touch for at least half a second, then release
   for one second within 30 seconds. Module must be active-high/momentary.
6. Confirm ALL 64 pixels are red, then green, then blue, then off: send `y` for
   each prompt; `n` rejects. Each prompt times out after 60 seconds. Send `x`
   during testing to stop. No green pass without these visual confirmations.
7. Green = these checks passed. Red = latched failure; read serial and unplug.
   Blue = working, yellow = idle/operator sensor steps. Unplug before swapping
   boards. Each board requires a fresh power-up and full test.

Matrix output is limited to 8/255 on one channel at a time (no white/full-load
sweep). Wi-Fi is disabled. This is not a measured or guaranteed current limit.
The divider is checked repeatedly against 4.5–5.5 V, including while waiting,
but ADC error/transients limit detection and no power switch is controlled.
An already-lit matrix may retain its old output until the tester sends clear.

PASS does not certify full-load capacity, external input operation, shorts on
unused pins, long-term reliability or enclosure operation. Matrix verification
is visual. Physical hardware tests remain outstanding until performed on each PCB.
