# Dragon firmware

ESP32-S3 SuperMini, 8×8 WS2812B matrix on GPIO12, TTP223 on GPIO11, LDR divider on GPIO9, supply divider on GPIO10. Microphone capture, I2S, audio effects, speech recognition and voice commands have been removed.

The new Dragon Kingdom connection prototype adds phone controls and local Wi-Fi
setup. See [WEB-SETUP.md](WEB-SETUP.md) for access credentials, the power-on
touch gesture, recovery behaviour and outstanding hardware acceptance checks.
Networking starts when the selected ceiling can cover controller, radio reserve
and panel idle. The 300 mA fallback keeps Wi-Fi off and retains touch lighting.
At higher passing levels, rendering leaves a provisional 50 mA Wi-Fi allowance.
The 400 mA estimated computer-USB ceiling is unchanged.

Profiles and on-device custom dragons are now available through Dragon Kingdom.
See [PROFILES-AND-CREATIONS.md](PROFILES-AND-CREATIONS.md) for editing, saved
startup preferences and the physical tap sequence based on favourites.

## Startup power selection

Every boot begins with a **2.5-second stabilization indication**: one dim blue face pixel blinks five times while the power rail and bulk capacitor settle. It adds about 1 mA in the current model, and no voltage measurements are taken during the indication. The matrix then remains fully dark for 300 ms before sampling. The firmware checks **300 and 400 mA estimated total load**, each using one bottom row at its corresponding intensity. It then tests **500, 800, 1600 and 2400 mA**, using the bottom 2, 4, 6 or 8 logical rows white. These gentle checks establish a fallback for supplies that cannot hold the 500 mA baseline. The pattern is capped to its estimated load: full-white rows would exceed the named load, so row intensity is limited. The estimate includes 200 mA for the controller and 64 mA panel idle. RGB channels never exceed 204/255.

After the stabilization delay, the ESP32-S3 checks its native USB D+/D− connection. If a computer/data host is present, the sweep stops after the tested 400 mA level and `computer_usb_cap=1` is reported. A later computer connection immediately lowers a larger session ceiling to 400 mA. The cap remains latched until restart, even if the serial monitor or cable is closed. A power-only USB charger does not enumerate as a computer, so it continues through the normal supply-capacity sweep.

Each level settles for 150 ms and collects 30 voltage samples over about 300 ms. Each sample is the median of five GPIO10 ADC readings. The 500 mA window supplies the low-side baseline. `power status` still prints minimum, maximum, mean, range and population standard deviation for every attempted level.

A level fails if:

- Its minimum is below 4.5 V.
- Above 500 mA, its minimum or mean is below 90% of the corresponding 500 mA baseline statistic.
- Above 500 mA, its low-side excursion (`mean - minimum`) exceeds max(3× the baseline low-side excursion, 0.150 V).
- A divider reading is invalid (below 3 V or above 6 V), or any reading exceeds the separate 5.5 V overvoltage ceiling.

The 300 mA, 400 mA and 500 mA checks establish safe fallbacks and must satisfy the absolute voltage floor. Levels above 500 mA also use its relative low-side baseline. A low or unstable result is unloaded and tested once more with a fresh sample window. If the repeat also fails, the last passing level is selected, including 300 or 400 mA. Invalid-divider and overvoltage results stop immediately without retry. Failure of the first 300 mA check inhibits normal lighting and shows a dim red diagnostic code (see SENSORS.md). All six passing selects 2400 mA. The accepted row pattern displays for **two seconds**, then the chosen dragon fades in.

The active ceiling and current-run statistics are RAM-only and recalculated at the next restart. The four most recent failed sweeps are additionally saved as one checksum-protected history in the separate `dragon-diag` NVS namespace, oldest to newest. A successful boot never erases or replaces this history. **Voltage sampling stops completely after startup**, including on failure. There is no later runtime sag protection. A short startup test cannot establish sustained supply capability or predict later cable/supply changes, and voltage plus a current model does not measure actual current or negotiate USB current.

## Brightness hierarchy

The renderer first caps the dragon to the session power ceiling, then multiplies by the faded ambient percentage, then the faded touch percentage. Each percentage is applied exactly once. Example: light 60% × touch 50% gives 30% of the power-capped LED output. Controller and LED idle current do not scale with brightness.

Both controls have ten nonzero targets: 10%, 20%, … 100%, with a separate off state. Intermediate values exist only during fades. Targets fade by one percentage point per 30 ms (300 ms for an adjacent step).

The LDR is sampled four times per second, only when automation is on. Ten ADC bins provide hybrid ambient lighting: in dark surroundings the LEDs dim to a gentle 10% floor, in normal room light output scales smoothly up to 100% so the dragon is clear and vivid, and superbright daylight stays at 100% ambient gain rather than switching off. Boundary hysteresis (24 ADC counts) and a one-second dwell prevent chatter. The saved calibration sets the dark floor and bright-room thresholds. `auto off` disables light automation explicitly (fixed 100% ambient gain). Touch never bypasses the ambient or power ceiling.

## Controls

- Single tap: next dragon; if off, restore previous lighting.
- Double tap: off/on.
- Hold: change touch brightness by 10 percentage points every 400 ms; direction alternates on release. Minimum is 10%; use double tap for off.
- The active profile, its starting glow, favourites and creations survive restart,
  along with Wi-Fi details, explicit LDR calibration and the sunrise schedule.
  Temporary play effects and glow changes do not replace the saved profile
  settings. Ambient and touch gains are recalculated during startup.

The catalog has 79 selectable dragons in 81 stable slots, based on the supplied
CSV with later documented colour corrections. IDs and order are locked for
saved-data compatibility; make additional creations through the phone editor. Wing edges and interiors are separate, editable regions. See DRAGON-PALETTES.md for import details and SENSORS.md for wiring.

Serial: 115200 baud, newline termination. Commands: `status`, `power status`, `sensors`, `dragons`, `dragon blue`, `palette 0..80`, `brightness 0..100` (rounded to ten-step targets), `auto on|off`, `light DARK BRIGHT`, `light calibrate COVERED ROOM`, `color R G B`, `mode zones|breathe|colorcycle|glitter|incendio|leviosa|solid|corners|chase|off`, `help`. `power status` prints the current run followed by the checksum-validated last saved failure.

Build with `python tools/dev.py build`; upload with `python tools/dev.py upload --port YOUR_PORT` after checking `ports`. The helper regenerates presets. Arduino-ESP32 3.2.1, Adafruit NeoPixel 1.12.5, 4 MB flash, 2 MB PSRAM, custom partitions. The former speech-model area is reserved and unused; no model is built, uploaded or read.

For an external-supply-only test, disconnect the ESP32 USB cable before restarting on the external supply. A connected computer USB cable may contribute power and invalidate the external-only result. The breakout, ESP32 5V/VBUS input, matrix and divider must share the intended supply and common ground.
