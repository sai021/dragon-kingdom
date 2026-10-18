// Low-light matrix-only test. Read README.md before connecting hardware.
#include <Adafruit_NeoPixel.h>

constexpr uint8_t MATRIX_PIN = 12;
constexpr uint8_t TOUCH_PIN = 11; // TTP223, active HIGH, momentary, 3.3V supply.
constexpr uint8_t STATUS_PIN = 48; // GPIO48 per user's supplied SuperMini pinout.
constexpr uint16_t PIXELS = 64;
constexpr uint8_t LEVEL = 8; // All pixels, ONE colour channel at a time. Never white.
constexpr uint32_t STEP_MS = 1000;
// Conservative project model: 200mA controller + 64mA panel idle +
// 64 * 20mA * 8/255 light + 5mA status allowance = about 310mA (<400mA).
// Estimate only; this is not measured current or short/inrush protection.
static_assert(200 + 64 + (PIXELS * 20 * LEVEL + 254) / 255 + 5 <= 400,
              "Pattern exceeds the project's estimated USB session ceiling");
Adafruit_NeoPixel matrix(PIXELS, MATRIX_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel indicator(1, STATUS_PIN, NEO_GRB + NEO_KHZ800);
uint8_t channel = 0;
uint32_t lastStep = 0;
bool paused = true;
bool touchRaw = false, touchStable = false, touchArmed = false, touchPressed = false;
uint32_t touchChanged = 0;

void showPattern() {
  matrix.fill(matrix.Color(channel == 0 ? LEVEL : 0,
                           channel == 1 ? LEVEL : 0, channel == 2 ? LEVEL : 0));
  matrix.show();
}
void status() {
  indicator.setPixelColor(0, paused ? 24 : 0, paused ? 12 : 0, paused ? 0 : 32);
  indicator.show();
}
void pauseTest() {
  paused = true; matrix.clear(); matrix.show();
  pinMode(MATRIX_PIN, OUTPUT); digitalWrite(MATRIX_PIN, LOW);
  status();
  Serial.println("PAUSED / AMBER: matrix dark, data LOW. 5V still LIVE; no hot-swap protection.");
}
void restartTest() {
  paused = false; channel = 0; status();
  // Brief settling interval before the first pattern.
  delay(300);
  showPattern(); lastStep = millis();
  Serial.println("RUNNING: RED, GREEN, BLUE. Tap/release touch to pause.");
}
void pollTouch() {
  bool value = digitalRead(TOUCH_PIN);
  if (value != touchRaw) { touchRaw = value; touchChanged = millis(); }
  if (millis() - touchChanged < 50) return;
  // Require an initial stable release; a held sensor at boot cannot start output.
  if (!touchArmed) {
    if (!value) { touchArmed = true; touchStable = false; }
    return;
  }
  if (value == touchStable) return;
  touchStable = value;
  if (value) touchPressed = true;
  else if (touchPressed) {
    touchPressed = false;
    if (paused) restartTest(); else pauseTest();
  }
}
void setup() {
  Serial.begin(115200);
  pinMode(TOUCH_PIN, INPUT_PULLDOWN);
  matrix.begin(); matrix.clear(); matrix.show();
  indicator.begin();
  // Visible startup diagnostic on the confirmed LED pin; matrix stays dark.
  for (uint8_t c = 0; c < 3; ++c) {
    indicator.setPixelColor(0, c == 0 ? 32 : 0, c == 1 ? 32 : 0, c == 2 ? 32 : 0);
    indicator.show(); delay(600);
  }
  status();
  // Allow the touch module to settle. No networking or NVS access.
  delay(1500);
  Serial.println("MATRIX TEST: all 64 pixels, dim RED then GREEN then BLUE; 3-second cycle.");
  Serial.println("64 pixels, GPIO12, GRB WS2812. Visually inspect every pixel/colour.");
  Serial.println("Starts PAUSED. Tap/release TTP223 to start or pause. x = pause; r = restart.");
  Serial.println("USB ONLY. External power disconnected. No automatic pass/fail.");
  pauseTest();
  touchRaw = digitalRead(TOUCH_PIN); touchChanged = millis();
}
void loop() {
  pollTouch();
  if (Serial.available()) {
    char c = Serial.read();
    if (c == 'x') {
      pauseTest();
    } else if (c == 'r') {
      restartTest();
    }
  }
  if (!paused && millis() - lastStep >= STEP_MS) {
    lastStep = millis();
    channel = (channel + 1) % 3;
    Serial.println(channel == 0 ? "RED" : channel == 1 ? "GREEN" : "BLUE");
    showPattern();
  }
}
