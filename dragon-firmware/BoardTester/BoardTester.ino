// Standalone assembly tester. See README.md before connecting a PCB.
// Pin mapping MUST match the built PCB. Does not access Wi-Fi or saved data.
#include <Adafruit_NeoPixel.h>

constexpr int LIGHT_PIN = 9, SUPPLY_PIN = 10, TOUCH_PIN = 11, MATRIX_PIN = 12;
constexpr int STATUS_PIN = 48; // Verify for YOUR S3 SuperMini revision first.
constexpr int PIXELS = 64;
Adafruit_NeoPixel statusLed(1, STATUS_PIN, NEO_GRB + NEO_KHZ800);
Adafruit_NeoPixel matrix(PIXELS, MATRIX_PIN, NEO_GRB + NEO_KHZ800);
bool failed = false, active = false;
float supplyV() {
  uint32_t sum = 0;
  for (int i = 0; i < 8; ++i) sum += analogReadMilliVolts(SUPPLY_PIN);
  return (sum / 8.0f) * 0.006f; // 100k upper / 20k lower divider
}
void colour(uint8_t r, uint8_t g, uint8_t b) {
  statusLed.setPixelColor(0, r, g, b); statusLed.show();
}
void fail(const char *reason) {
  if (failed) return;
  failed = true;
  matrix.clear(); matrix.show(); colour(12, 0, 0);
  Serial.print("FAIL (latched): "); Serial.println(reason);
  Serial.println("Unplug USB before inspecting. Reset to retest; never hot-swap PCB.");
}
bool guard() {
  if (failed) return false;
  float v = supplyV();
  if (v < 4.5f || v > 5.5f) {
    Serial.print("Divider-estimated rail V = "); Serial.println(v, 3);
    fail("Supply outside 4.5-5.5 V, or incorrect divider/wiring.");
  }
  return !failed;
}
bool waitSafe(uint32_t duration) {
  uint32_t start = millis();
  while (millis() - start < duration) {
    if (!guard()) return false;
    if (Serial.available() && Serial.read() == 'x') {
      fail("Operator stopped test."); return false;
    }
    delay(20);
  }
  return true;
}
bool answer(const char *prompt) {
  while (Serial.available()) Serial.read();
  Serial.println(prompt); Serial.println("Send y to confirm; n or x to fail. Timeout 60 seconds.");
  uint32_t start = millis();
  while (millis() - start < 60000) {
    if (!guard()) return false;
    if (Serial.available()) {
      char c = Serial.read();
      if (c == 'y') return true;
      if (c == 'n' || c == 'x') { fail("Visual check rejected."); return false; }
    }
    delay(20);
  }
  fail("Visual confirmation timed out."); return false;
}
void runTests() {
  active = true; colour(0, 0, 10);
  matrix.begin(); matrix.clear(); matrix.show();
  if (!waitSafe(3000)) return;
  Serial.print("Supply estimate V: "); Serial.println(supplyV(), 3);
  colour(10, 6, 0);
  Serial.println("LDR: cover for 3 seconds, then shine room light on it. You have 20 seconds.");
  int low = 4095, high = 0;
  uint32_t start = millis(), report = 0;
  while (millis() - start < 20000) {
    if (!waitSafe(50)) return;
    int value = analogRead(LIGHT_PIN);
    low = min(low, value); high = max(high, value);
    if (millis() - report >= 1000) {
      report = millis(); Serial.print("LDR raw: "); Serial.println(value);
    }
  }
  Serial.print("LDR range: "); Serial.print(low); Serial.print(" .. "); Serial.println(high);
  if (high - low < 400) { fail("LDR change below 400 counts. Check lighting and divider."); return; }
  Serial.println("Touch: release for one second, touch for half a second, then release for one second.");
  int phase = 0;
  uint32_t stable = millis(); start = millis();
  while (phase < 3 && millis() - start < 30000) {
    if (!waitSafe(20)) return;
    bool expected = phase == 1; // TTP223 active HIGH, momentary configuration
    if (bool(digitalRead(TOUCH_PIN)) != expected) stable = millis();
    else if (millis() - stable >= (phase == 1 ? 500UL : 1000UL)) {
      ++phase; stable = millis(); Serial.print("Touch stage passed: "); Serial.println(phase);
    }
  }
  if (phase != 3) { fail("Touch sequence timed out. Check TTP223 wiring/configuration."); return; }
  colour(0, 0, 10);
  const uint8_t rgb[3][3] = {{8,0,0},{0,8,0},{0,0,8}};
  const char *prompts[] = {"Are ALL 64 pixels RED, with no missing/flickering pixels?",
                          "Are ALL 64 pixels GREEN, with no missing/flickering pixels?",
                          "Are ALL 64 pixels BLUE, with no missing/flickering pixels?"};
  for (int c = 0; c < 3; ++c) {
    matrix.fill(matrix.Color(rgb[c][0], rgb[c][1], rgb[c][2])); matrix.show();
    if (!answer(prompts[c])) return;
  }
  matrix.clear(); matrix.show();
  if (!answer("Is the entire matrix now OFF?")) return;
  if (!guard()) return;
  colour(0, 12, 0);
  Serial.println("PASS: supply at light load, LDR change, touch sequence and operator-confirmed matrix checks.");
  Serial.println("Not a short-circuit protector, current measurement or full-load supply certification.");
  Serial.println("Unplug USB before removing this PCB. Reset and repeat for every board.");
}
void setup() {
  pinMode(TOUCH_PIN, INPUT_PULLDOWN);
  pinMode(MATRIX_PIN, INPUT); // No matrix data until operator starts.
  analogReadResolution(12);
  analogSetPinAttenuation(SUPPLY_PIN, ADC_11db);
  analogSetPinAttenuation(LIGHT_PIN, ADC_11db);
  statusLed.begin(); colour(10, 6, 0);
  Serial.begin(115200);
}
void loop() {
  static uint32_t lastPrompt = 0;
  if (!active && millis() - lastPrompt > 2000) {
    lastPrompt = millis();
    Serial.println("PCB TESTER: complete unpowered multimeter checks first. USB ONLY; external power disconnected.");
    Serial.println("Send g to start, x to stop during testing. Confirm onboard LED is yellow before starting.");
  }
  if (!active && Serial.available() && Serial.read() == 'g') runTests();
  if (active && !failed) guard();
  delay(20);
}
