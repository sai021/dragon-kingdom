// Native simulation of C3 pin selection and hardware-CDC power detection.
#define CONFIG_IDF_TARGET_ESP32C3 1
#define ARDUINO_USB_MODE 1
#define ARDUINO_USB_CDC_ON_BOOT 1
struct HWCDC {
 inline static bool connected = true;
 static bool isPlugged(){return connected;}
};
#include "../DragonPrototype/DragonPrototype.ino"
#include <cassert>
int main(){
 static_assert(Config::DATA_PIN==3 && Config::TOUCH_PIN==2);
 static_assert(Config::LIGHT_PIN==0 && Config::VOLTAGE_PIN==1);
 assert(computerUsbConnected());
 startupCheck();
 assert(computerUsbMode && operatingTotal<=400);
 HWCDC::connected=false;
 assert(!computerUsbConnected());
 // Attaching a host during a session must also enforce the existing cap.
 computerUsbMode=false;operatingTotal=2400;HWCDC::connected=true;delay(251);
 loop();
 assert(computerUsbMode && operatingTotal<=400);
 puts("PASS: simulated C3 pin map, USB detection and 400mA session ceiling.");
}
