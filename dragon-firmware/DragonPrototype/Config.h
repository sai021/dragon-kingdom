#pragma once
#include <stdint.h>

#ifndef DRAGON_USE_TTP223
#define DRAGON_USE_TTP223 1
#endif
namespace Config {
#if defined(CONFIG_IDF_TARGET_ESP32C3)
// Same eight power-side header positions as the documented S3 carrier.
constexpr uint8_t LIGHT_PIN = 0;
constexpr uint8_t DATA_PIN = 3;
constexpr uint8_t TOUCH_PIN = 2; // Strapping pin: verify TTP223 startup physically.
constexpr uint8_t VOLTAGE_PIN = 1;
#else
constexpr uint8_t LIGHT_PIN = 9;
constexpr uint8_t DATA_PIN = 12;
constexpr uint8_t TOUCH_PIN = 11;
// 5 V -> 100k -> GPIO10 -> 20k -> GND; 100 nF from GPIO10 to GND.
constexpr uint8_t VOLTAGE_PIN = 10;
#endif
constexpr uint8_t MATRIX_WIDTH = 8;
constexpr uint16_t MATRIX_COUNT = MATRIX_WIDTH * MATRIX_WIDTH;
constexpr float DIVIDER_HIGH_OHMS = 100000.0f;
constexpr float DIVIDER_LOW_OHMS = 20000.0f;
// Provisional transfer from the previous ESP32/divider. Recheck against a meter.
constexpr float VOLTAGE_CALIBRATION = 1.0135f;
constexpr uint8_t MAX_CHANNEL_OUTPUT = 204;
// 8.5 dBm: the USB-powered S3 joined the test router at this setting after
// repeated missing-authentication-ACK failures at the library default.
// Range and C3 radio behaviour still require physical validation.
constexpr int8_t WIFI_TX_QUARTER_DBM = 34;
constexpr uint16_t ESP_RESERVE_MA = 200;
constexpr uint16_t WIFI_RESERVE_MA = 50;
constexpr uint16_t PANEL_IDLE_MA = MATRIX_COUNT;
constexpr uint16_t MIN_TOTAL_MA = 300;
constexpr uint16_t DEFAULT_MAX_TOTAL_MA = 2400;
constexpr uint32_t FRAME_MS = 33;
constexpr uint32_t TOUCH_SAMPLE_MS = 20;
constexpr uint32_t TOUCH_DEBOUNCE_MS = 50;
constexpr uint32_t HOLD_MS = 700;
constexpr uint32_t DIM_STEP_MS = 400;
constexpr float TOUCH_ON_RATIO = 1.25f;
constexpr float TOUCH_OFF_RATIO = 1.10f;
}
