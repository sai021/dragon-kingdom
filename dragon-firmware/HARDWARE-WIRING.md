# Dragon hardware and wiring

## User-confirmed completed enclosure — 19 October 2026

The assembled hardware is made. Normal users have access to the bottom USB-C
power port and the touch button on the right side. The internal ESP32 USB-C
connector is not accessible to the user. A keyhole-shaped mounting slot is on
the back; the motto surrounds the dragon except along the bottom.

Newer STL files, build photos and Gerbers are still to be supplied. Existing
repository CAD/PCB assets remain earlier prototypes, not a substitute for those
updated files. This layout confirmation does not replace the separately listed
external-supply/current/thermal and optical validation.

## Installed parts

| Part | Value / role | Connection |
|---|---|---|
| ESP32-S3 SuperMini | Controller | See GPIO table below |
| WS2812B matrix | 8×8, 64 addressable RGB LEDs | 5 V, GND, DIN from GPIO12 |
| TTP223 module | Capacitive touch sensor | 3.3 V, GND, OUT to GPIO11 |
| LDR | Ambient-light sensor | Upper half of the 3.3 V light divider |
| Resistor | 10 kΩ | GPIO9/LDR junction to GND |
| Resistor | 100 kΩ | 5 V rail to GPIO10 supply-sense junction |
| Resistor | 20 kΩ | GPIO10 supply-sense junction to GND |
| Ceramic capacitor | 100 nF | GPIO10 supply-sense junction to GND |
| Ceramic capacitor | 100 nF, recommended | GPIO9 LDR junction to GND for additional ADC filtering |
| Ceramic capacitor | 100 nF, recommended | Directly across TTP223 VCC and GND |
| Bulk electrolytic capacitor | 1000 µF, at least 6.3 V (10 V preferred) | Across matrix 5 V and GND; observe polarity |
| USB-C breakout | 5 V sink; 5.1 kΩ Rd on CC1 and CC2 | External 5 V input; D+/D− unused for power |

The INMP441 microphone is no longer used by the firmware.

### Confirmed power arrangement — 14 October 2026

During development, the laptop USB-C cable powers the circuit through the
ESP32 USB connector. The external/main power input is disconnected. Keep the
firmware's computer-USB ceiling at 400 mA for this arrangement.

In the deployed product, the ESP32 sits inside the enclosure. The product's
external supply powers the matrix directly through the shared 5 V rail;
matrix current is not intended to pass through the ESP32 USB connector or
board. The controller shares the intended supply and common ground.

Never connect laptop USB power and external/main power simultaneously in the
current circuit. Laptop-powered tests do not establish the external supply's
capacity or deployed brightness. Disconnect laptop USB before testing the
external supply.

## GPIO assignment

The default build is S3. The optional C3 build preserves the eight power-side
header positions in the supplied SuperMini pinouts, subject to actual footprint
and orientation verification. Its assignments are matrix GPIO3, TTP223 GPIO2,
LDR GPIO0/ADC1_CH0 and voltage GPIO1/ADC1_CH1; GPIO4 is unused. Power pins are
5V, GND and 3V3. C3 GPIO2 is a strapping pin: cold-start/setup-gesture behaviour
with the TTP223 must be checked physically. On 19 October the user-confirmed
carrier pin orientation, normal cold USB startup, visible lighting, touch, LDR
response and 400 mA USB limiting passed. Startup with touch held also passed:
the user saw normal lighting and setup Wi-Fi on their phone, and post-boot
serial/HTTP confirmed the AP and home connection. This evidence applies to
the tested prototype carrier, not final PCB
fit or external-supply validation. See [physical results](../docs/HARDWARE-TEST-2026-10-19.md).

| ESP32-S3 pin | Function |
|---|---|
| GPIO12 | WS2812B matrix data |
| GPIO11 | TTP223 digital output |
| GPIO9 / ADC1_CH8 | LDR divider junction |
| GPIO10 / ADC1_CH9 | 5 V supply-divider junction |
| 3V3 | TTP223 and LDR divider supply |
| 5V/VBUS | Matrix/external 5 V rail |
| GND | Common ground for every part |

## Circuit

```text
                 POWER — USE ONE SOURCE AT A TIME

  PC USB-C ───────> ESP32 USB connector
                         │ onboard 5V/VBUS
                         └───────────────┐
                                         ├──── +5V RAIL ───────────────┐
  External USB-C breakout VBUS ──────────┘                              │
  (CC1 ─ 5.1k ─ GND, CC2 ─ 5.1k ─ GND; D+/D− unused)                   │
                                                                         │
                  ┌──────────────────────────────────────────────────────┤
                  │                                                      │
                  │       100k                                           │
                  ├──────/\/\/\/──────●──────── GPIO10 (voltage ADC)     │
                  │                  divider junction                     │
                  │                         │                             │
                  │                    ┌────┴────┐                        │
                  │                   20k      100nF                      │
                  │                    │         │                        │
                  │                    └────┬────┘                        │
                  │                         │                             │
                  │                        GND                            │
                  │                                                      │
                  ├──────────── WS2812B 8×8 +5V                         │
                  │                    GND ─────────── GND                │
                  │                    DIN <── 330–470Ω <── GPIO12        │
                  │                                                      │
                  └──────── (+) 1000µF (−) ─────────── GND              │
                                                                         │
  ESP32 3V3 ──────●────────────── TTP223 VCC                             │
                  ├──── 100nF ───────────── GND (place near TTP223)      │
                  └──── LDR ─────●──────── GPIO9 (light ADC)             │
                              LDR junction                               │
                                    ├──── 10k ─────────────────── GND    │
                                    └──── 100nF ───────────────── GND    │
                                          (optional ADC filter)          │
                                                                         │
  TTP223 GND ──────────────────────────────────────────────────── GND    │
  TTP223 OUT ───────────────────────────────────────────────── GPIO11    │
                                                                         │
  ALL GND POINTS ───────────────── COMMON GROUND ────────────────────────┘
```

The 330–470 Ω matrix data resistor is recommended close to the matrix DIN. A 74AHCT125 powered from 5 V can be added as a 3.3 V-to-5 V data level shifter if the matrix data connection is unreliable.

Do not connect the computer's USB 5 V and the external break-out 5 V at the same time unless a proper power multiplexer, ideal-diode circuit, or equivalent source isolation is installed. Their grounds may be common.

## Checked voltages

For the supply divider:

```text
GPIO10 = VBUS × 20k / (100k + 20k) = VBUS / 6
```

Therefore GPIO10 should be about 0.833 V at 5.00 V VBUS and 0.850 V at 5.10 V VBUS. A reading near 4.2 V indicates the 100 kΩ and 20 kΩ resistors are reversed. The earlier replacement-board reading of roughly 2.72–2.95 V was from the previous GPIO9 circuit and is retained only as historical diagnostic evidence.
