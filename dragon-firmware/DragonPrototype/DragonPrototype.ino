#include <Arduino.h>
#include <Adafruit_NeoPixel.h>
#include <Preferences.h>
#include <math.h>
#include <stdlib.h>
#include <string.h>
#include "PowerPolicy.h"
#include "DragonPresets.h"
#include "SensorControl.h"
#include "StartupPower.h"
#include "ConnectionPolicy.h"
#include "DragonLibrary.h"
#include "SunriseAlarm.h"
#ifdef ARDUINO
#include <time.h>
#include <sys/time.h>
#endif

#if !defined(CONFIG_IDF_TARGET_ESP32S3) && !defined(CONFIG_IDF_TARGET_ESP32C3)
#error "Select ESP32S3 Dev Module or ESP32C3 Dev Module."
#endif
#if defined(CONFIG_IDF_TARGET_ESP32C3) && !DRAGON_USE_TTP223
#error "The C3 requires the external TTP223; native capacitive touch is unavailable."
#endif
#if defined(ARDUINO) && (!ARDUINO_USB_MODE || !ARDUINO_USB_CDC_ON_BOOT)
#error "Hardware USB CDC on boot is required for computer USB power limiting."
#endif

using namespace Dragon;
Adafruit_NeoPixel pixels(PHYSICAL_COUNT,Config::DATA_PIN,NEO_GRB+NEO_KHZ800);
Wiring wiring;
DragonLibrary::Library library;
DragonPreset currentPreset=DRAGON_PRESETS[DEFAULT_PRESET];
TouchFilter nativeTouch;
RGB frame[PHYSICAL_COUNT],zoneColors[ZONE_COUNT];
uint16_t zoneGain[ZONE_COUNT],pixelGain[64];

enum Mode : uint8_t {
 ZONE_VIEW,BREATHE,COLOR_CYCLE,PATRONUS_GLITTER,INCENDIO,LEVIOSA,SOLID,CORNERS,CHASE,OFF
};
Mode mode=ZONE_VIEW;
RGB solidColor={255,160,80};
uint8_t brightness=50,palette=0;
uint16_t operatingTotal=0,estimatedMa=Config::PANEL_IDLE_MA;
uint32_t lastFrame=0,lastTouch=0,lastReport=0;
bool telemetry=true,dimUp=false;
AmbientLight ambient;
TouchGestures gestures;
StartupPower startupPower;
bool autoLight=true;
bool computerUsbMode=false;
DragonAlarm::Alarm sunrise;
Preferences alarmStore;
bool alarmStoreReady=false;
#ifndef ARDUINO
int64_t simulatedAlarmEpoch=0;
#endif
int64_t alarmEpoch(){
#ifdef ARDUINO
 return int64_t(time(nullptr));
#else
 return simulatedAlarmEpoch;
#endif
}
void loadAlarmSettings(){
 alarmStoreReady=alarmStore.begin("dragon-alarm",false);
 DragonAlarm::Settings saved{};
 if(alarmStoreReady&&alarmStore.getBytesLength("settings")==sizeof(saved)&&
    alarmStore.getBytes("settings",&saved,sizeof(saved))==sizeof(saved)&&
    DragonAlarm::valid(saved)&&saved.check==DragonAlarm::checksum(saved))sunrise.apply(saved);
}
bool saveAlarmSettings(DragonAlarm::Settings value){
 if(!DragonAlarm::valid(value))return false;
 if(!alarmStoreReady)alarmStoreReady=alarmStore.begin("dragon-alarm",false);
 value.check=DragonAlarm::checksum(value);DragonAlarm::Settings verify{};
 if(!alarmStoreReady||alarmStore.putBytes("settings",&value,sizeof(value))!=sizeof(value)||
    alarmStore.getBytes("settings",&verify,sizeof(verify))!=sizeof(verify)||
    memcmp(&value,&verify,sizeof(value)))return false;
 sunrise.apply(value);return true;
}
bool setupRequested=false;
DragonConnection::StartupHold setupHold;
uint8_t touchGain=100;
uint8_t ambientGain=100;
uint32_t lastLight=0,lastFade=0,lastUsbCheck=0,touchPresses=0;

Preferences lightStore,diagnosticStore;
struct LightSettings {uint32_t magic;uint16_t dark,bright;uint32_t check;};
bool lightStoreReady=false,lightCalibrated=false;
bool diagnosticStoreReady=false,savedFailureValid=false,failureSavedThisBoot=false;
SavedPowerFailure savedFailure{};
SavedFailureHistory failureHistory{};
uint32_t lightChecksum(uint16_t dark,uint16_t bright){return 0x4c445231u^(uint32_t(dark)<<16)^bright;}
void loadLightSettings(){
 lightStoreReady=lightStore.begin("dragon-light",false);
 LightSettings saved{};
 if(lightStoreReady&&lightStore.getBytesLength("settings")==sizeof(saved)&&
 lightStore.getBytes("settings",&saved,sizeof(saved))==sizeof(saved)&&saved.magic==0x4c445231u&&
 saved.dark<saved.bright&&saved.bright<=4095&&saved.check==lightChecksum(saved.dark,saved.bright)){
  ambient.dark=saved.dark;ambient.bright=saved.bright;lightCalibrated=true;
 }
}
bool saveLightSettings(uint16_t dark,uint16_t bright){
 if(dark>=bright||bright>4095)return false;
 if(!lightStoreReady)lightStoreReady=lightStore.begin("dragon-light",false);
 LightSettings saved{0x4c445231u,dark,bright,lightChecksum(dark,bright)},check{};
 if(!lightStoreReady||lightStore.putBytes("settings",&saved,sizeof(saved))!=sizeof(saved)||
 lightStore.getBytes("settings",&check,sizeof(check))!=sizeof(check)||memcmp(&saved,&check,sizeof(saved)))return false;
 ambient.dark=dark;ambient.bright=bright;ambient.candidate=ambient.night;ambient.candidateSince=millis();
 lightCalibrated=true;return true;
}
const char* startupResult="not run";
char commandLine[256];size_t commandLength=0;bool lineOverflow=false;
bool networkSerialCommand(char* line);

struct LightingState {Mode mode;uint8_t brightness,palette;RGB solid;};
LightingState resumeState={ZONE_VIEW,100,0,{255,160,80}};

void setPalette(uint8_t p) {
 sunrise.stop();
 palette=DragonLibrary::selectable(library.data,p,library.data.active)?p:DEFAULT_PRESET;
 currentPreset=library.resolve(palette);
 for(int z=0;z<ZONE_COUNT;z++)zoneColors[z]=currentPreset.zones[z];
}

void setBrightness(uint8_t value) {
 sunrise.stop();
 brightness=value?min(100,((int(value)+5)/10)*10):0;
 if(value&&brightness==0)brightness=10;
}
void manualControl(){autoLight=false;ambientGain=100;}
void rememberLighting(){if(mode!=OFF&&brightness)resumeState={mode,brightness,palette,solidColor};}
void wakeLighting(){
 mode=resumeState.mode;setPalette(resumeState.palette);solidColor=resumeState.solid;
 setBrightness(resumeState.brightness?resumeState.brightness:100);
}
void toggleLighting(){
 if(sunrise.active){sunrise.stop();return;}
 bool off=mode==OFF||brightness==0;
 if(off){wakeLighting();}else{rememberLighting();mode=OFF;setBrightness(0);}
}
void updateLight(uint32_t now){
 // Four ADC reads per second; no ADC work at all when automation is off.
 if(autoLight&&uint32_t(now-lastLight)>=250){lastLight=now;ambient.update(analogRead(Config::LIGHT_PIN),now);}
 if(uint32_t(now-lastFade)>=30){
  lastFade=now;
  uint8_t target=autoLight?ambient.targetGain():100;
  if(ambientGain<target)ambientGain++;else if(ambientGain>target)ambientGain--;
  if(touchGain<brightness)touchGain++;else if(touchGain>brightness)touchGain--;
 }
}

uint32_t hashPixel(uint32_t value) {
 value^=value>>16;value*=0x7feb352du;value^=value>>15;value*=0x846ca68bu;return value^(value>>16);
}
RGB mixRgb(RGB a,RGB b,uint8_t amount) {
 return {uint8_t((uint16_t(a.r)*(255-amount)+uint16_t(b.r)*amount)/255),
         uint8_t((uint16_t(a.g)*(255-amount)+uint16_t(b.g)*amount)/255),
         uint8_t((uint16_t(a.b)*(255-amount)+uint16_t(b.b)*amount)/255)};
}
// Add sparkle light rather than blending away a bright base channel.
RGB sparkleRgb(RGB base,RGB accent,uint8_t amount) {
 RGB light=scaled(accent,amount,255);
 return {clampByte(uint16_t(base.r)+light.r),clampByte(uint16_t(base.g)+light.g),clampByte(uint16_t(base.b)+light.b)};
}
RGB hueRgb(uint16_t hue) {
 uint8_t region=(hue/256)%6,position=hue&255;
 switch(region){
  case 0:return {255,position,0};case 1:return {uint8_t(255-position),255,0};
  case 2:return {0,255,position};case 3:return {0,uint8_t(255-position),255};
  case 4:return {position,0,255};default:return {255,0,uint8_t(255-position)};
 }
}
bool wingZone(Zone z){return z==LW||z==RW;}
bool fullWingZone(Zone z){return wingZone(z)||z==LE||z==RE;}

// Per-dragon animation layers apply only to their selected regions.
RGB presetColor(RGB c,Zone z,int x,int y,uint32_t now) {
 const DragonPreset& p=currentPreset;
 if(!(p.animatedZones&(1u<<z)))return c;
 const float phase=float(now%p.periodMs)/p.periodMs;
 if((p.effects&PRESET_CYCLE)&&(p.effectZones[0]&(1u<<z)))
  c=mixRgb(c,hueRgb(uint16_t(phase*1536+(x+y)*60)),180);
 if((p.effects&PRESET_SHIMMER)&&(p.effectZones[2]&(1u<<z))){
  float wave=.5f+.5f*sinf(phase*6.2831853f+x*.65f+y*.4f);
  c=mixRgb(c,p.accent,uint8_t(wave*p.shimmerAmount*255/100));
 }
 if((p.effects&PRESET_GLITTER)&&(p.effectZones[3]&(1u<<z))){
  // Smooth rise/fall at both ends of each sparkle; different pixel phases
  // avoid synchronised wing flashes when the random selection changes.
  uint32_t span=p.periodMs/2;
  uint32_t clock=now+hashPixel(y*8+x)%span;
  uint32_t key=hashPixel((clock/span)*131+y*8+x);
  float envelope=sinf(float(clock%span)/span*3.14159265f);
  if(key%100<p.glitterPercent)c=sparkleRgb(c,p.accent,uint8_t(envelope*envelope*255));
 }
 if((p.effects&PRESET_BREATHE)&&(p.effectZones[1]&(1u<<z))){
  uint16_t level=uint16_t(p.breatheMin+(100-p.breatheMin)*(.5f+.5f*sinf(phase*6.2831853f)));
  c=visibleScale(c,level,100);
 }
 return c;
}

void composeFrame(uint32_t now) {
 clear(frame);
 // Keep a failed standalone startup diagnosable without USB power or a fast meter.
 // Eight very dim red pixels add only about 10 mA in the current model.
 if(!operatingTotal&&startupPower.failure){
  uint32_t phase=now%(uint32_t(startupPower.failure)*1000+2000);
  if(phase<uint32_t(startupPower.failure)*1000&&phase%1000<500)
   for(int x=0;x<8;x++)frame[logicalIndex(x,7,wiring)]={16,0,0};
  estimatedMa=estimatedMilliAmps(frame);return;
 }
 const uint16_t breathe=uint16_t(35+65*(.5f+.5f*sinf(now*.0015f)));
 for(int y=0;y<8;y++)for(int x=0;x<8;x++){
  Zone z=ZONES[y][x];RGB c={0,0,0};
  if(mode==ZONE_VIEW||mode==BREATHE||mode==PATRONUS_GLITTER||mode==LEVIOSA)c=currentPreset.pixels[y*8+x];
  else if(mode==COLOR_CYCLE)c=mixRgb(zoneColors[z],hueRgb(uint16_t(now/12+(x+y)*80)),110);
  else if(mode==INCENDIO){
   uint8_t flicker=uint8_t(150+hashPixel((now/70)*97+y*8+x)%106);
   c=scaled((y<3?RGB{255,190,30}:RGB{255,45,0}),flicker,255);
  } else if(mode==SOLID)c=solidColor;
  else if(mode==CHASE&&int((now/220)%64)==y*8+x)c={255,255,255};
  else if(mode==CORNERS){
   if(x==0&&y==0)c={255,0,0};if(x==7&&y==0)c={0,255,0};
   if(x==7&&y==7)c={0,0,255};if(x==0&&y==7)c={255,255,255};
  }
  if(mode==ZONE_VIEW)c=presetColor(c,z,x,y,now);
  if(mode==BREATHE)c=visibleScale(c,breathe,100);
  if(mode==PATRONUS_GLITTER&&fullWingZone(z)){
   uint32_t age=now%420,key=hashPixel((now/420)*131+y*8+x);
   // Hold the white peak before fading so a sparkle is easier to see.
   uint8_t strength=age<90?255:uint8_t(255-(age-90)*255/330);
   if(key%100<20)c=sparkleRgb(c,{255,255,255},strength);
  }
  if(mode==LEVIOSA&&wingZone(z)){
   uint32_t phase=(now/55+uint32_t(7-y)*3+x*5)%31;
   if(phase<4)c=mixRgb(c,{255,255,255},uint8_t(255-phase*45));
  }
  if(sunrise.active){
   // Both wing interiors and wing edges glow from deep orange to warm white.
   bool wing=fullWingZone(z);
   RGB dawn=mixRgb({255,35,0},{255,220,150},uint8_t(sunrise.level*255/1000));
   c=wing?visibleScale(dawn,sunrise.level,1000):RGB{0,0,0};
  }
  c=visibleScale(c,Config::MAX_CHANNEL_OUTPUT,255);
  if(!sunrise.active&&mode!=SOLID&&mode!=CORNERS&&mode!=CHASE&&mode!=OFF){
   c=scaled(c,zoneGain[z],100);c=scaled(c,pixelGain[y*8+x],100);
  }
  c.r=min(c.r,Config::MAX_CHANNEL_OUTPUT);c.g=min(c.g,Config::MAX_CHANNEL_OUTPUT);c.b=min(c.b,Config::MAX_CHANNEL_OUTPUT);
  int index=logicalIndex(x,y,wiring);if(index>=0)frame[index]=c;
 }
 if(operatingTotal<BASE_TOTAL_MA)clear(frame);
 // Additional provisional allowance for Wi-Fi; verify on the actual supply.
 else capVisibleCurrent(frame,operatingTotal-runtimeReserve(operatingTotal));
 // Exactly one scaling per hierarchy level: session power -> ambient -> touch.
 if(!sunrise.active)for(auto& pixel:frame){
  pixel=scaled(pixel,ambientGain,100);
  pixel=scaled(pixel,touchGain,100);
 }
 estimatedMa=estimatedMilliAmps(frame);
}
void showFrame() {
 for(int i=0;i<PHYSICAL_COUNT;i++)pixels.setPixelColor(i,frame[i].r,frame[i].g,frame[i].b);
 pixels.show();
}
void render(uint32_t now) {
 if(uint32_t(now-lastFrame)<Config::FRAME_MS)return;lastFrame=now;composeFrame(now);showFrame();
}

const char* failureName(uint8_t failure){
 const char* names[]={"none","low voltage","invalid divider reading","downward voltage instability","incomplete samples","overvoltage"};
 return failure<=5?names[failure]:"unknown";
}
void loadSavedFailure(){
 diagnosticStoreReady=diagnosticStore.begin("dragon-diag",false);
 SavedFailureHistory history{};
 if(diagnosticStoreReady&&diagnosticStore.getBytesLength("history")==sizeof(history)&&
    diagnosticStore.getBytes("history",&history,sizeof(history))==sizeof(history)&&validFailureHistory(history)){
  failureHistory=history;savedFailureValid=history.count>0;
 }else{
  // Import the one-record format used by the first diagnostic build in RAM.
  SavedPowerFailure legacy{};
  if(diagnosticStoreReady&&diagnosticStore.getBytesLength("failure")==sizeof(legacy)&&
     diagnosticStore.getBytes("failure",&legacy,sizeof(legacy))==sizeof(legacy)&&validFailureRecord(legacy)){
   appendFailure(failureHistory,legacy);savedFailureValid=true;
  }
 }
 if(savedFailureValid){
  uint8_t latest=(failureHistory.next+SavedFailureHistory::CAPACITY-1)%SavedFailureHistory::CAPACITY;
  savedFailure=failureHistory.records[latest];
 }
}
bool saveStartupFailure(){
 if(!startupPower.failure)return false;
 if(!diagnosticStoreReady)diagnosticStoreReady=diagnosticStore.begin("dragon-diag",false);
 SavedPowerFailure candidate=makeFailureRecord(startupPower);
 SavedFailureHistory updated=failureHistory,check{};appendFailure(updated,candidate);
 bool ok=diagnosticStoreReady&&
  diagnosticStore.putBytes("history",&updated,sizeof(updated))==sizeof(updated)&&
  diagnosticStore.getBytes("history",&check,sizeof(check))==sizeof(check)&&
  !memcmp(&updated,&check,sizeof(updated))&&validFailureHistory(check);
 if(ok){failureHistory=check;savedFailure=candidate;savedFailureValid=true;}
 failureSavedThisBoot=ok;return ok;
}
void printSavedFailure(){
 if(!savedFailureValid){Serial.println("saved_failures=none");return;}
 Serial.printf("saved_failures=%u capacity=%u oldest_to_newest=1\n",failureHistory.count,SavedFailureHistory::CAPACITY);
 uint8_t oldest=(failureHistory.next+SavedFailureHistory::CAPACITY-failureHistory.count)%SavedFailureHistory::CAPACITY;
 for(uint8_t entry=0;entry<failureHistory.count;entry++){
  const auto& failure=failureHistory.records[(oldest+entry)%SavedFailureHistory::CAPACITY];
  Serial.printf("saved_failure_entry=%u code=%u reason=%s tested=%u fallback_max=%umA last_sample_volts=%.3f\n",
   entry+1,failure.failure,failureName(failure.failure),failure.tested,failure.maximum,failure.lastVolts);
  for(uint8_t i=0;i<failure.tested;i++){
   const auto& v=failure.stats[i];
   Serial.printf("saved entry=%u level=%umA samples=%u min=%.3f max=%.3f mean=%.3f range=%.3f stddev=%.3f\n",
    entry+1,StartupPower::levels[i],v.count,v.minimum,v.maximum,v.mean,v.range,v.deviation);
  }
 }
}

void printPowerStats(){
 for(uint8_t i=0;i<startupPower.tested;i++){
  const auto& v=startupPower.stats[i];
  Serial.printf("startup level=%umA samples=%u min=%.3f max=%.3f mean=%.3f range=%.3f stddev=%.3f\n",
   StartupPower::levels[i],v.count,v.minimum,v.maximum,v.mean,v.range(),v.deviation());
 }
 Serial.printf("session_max=%umA result=%s computer_usb_cap=%u voltage_sampling=stopped\n",operatingTotal,startupResult,computerUsbMode);
 Serial.printf("startup_failure=%u last_sample_volts=%.3f\n",startupPower.failure,startupPower.lastVolts);
 Serial.printf("failure_saved_this_boot=%u\n",failureSavedThisBoot);
 printSavedFailure();
}
void startupStabilize(){
 // One dim blue channel adds about 1 mA in the model. Voltage is not sampled
 // during this indication; finish fully dark and allow 300 ms more settling.
 for(uint8_t pulse=0;pulse<5;pulse++){
  clear(frame);frame[logicalIndex(3,2,wiring)]={0,0,12};showFrame();delay(200);
  pixels.clear();pixels.show();delay(300);
#if DRAGON_USE_TTP223
  // Ignore the sensor's first 500 ms, then require a continuous two-second hold.
  setupHold.observe(digitalRead(Config::TOUCH_PIN)!=0,millis());
  setupRequested=setupHold.requested;
#endif
 }
 clear(frame);pixels.clear();pixels.show();delay(300);
}
bool computerUsbConnected(){
#if ARDUINO_USB_MODE && ARDUINO_USB_CDC_ON_BOOT
 return HWCDC::isPlugged();
#else
 return false;
#endif
}
void startupCheck(int8_t computerOverride=-1) {
 startupPower=StartupPower{};operatingTotal=0;
 pixels.clear();pixels.show();
 startupStabilize();
 // Detect after the stabilization indication so the host has time to enumerate.
 computerUsbMode=computerOverride>=0?computerOverride:computerUsbConnected();
 const uint8_t levelCount=computerUsbMode?2:StartupPower::LEVEL_COUNT;
 for(uint8_t level=0;level<levelCount;level++){
  bool accepted=false;
  for(uint8_t attempt=0;attempt<2;attempt++){
   startupPower.stats[level]=VoltageStats{};
   startupPower.failure=0;startupPower.result="testing";
   startupPower.pattern(frame,level,wiring);showFrame();
   delay(150); // Settle the new load before comparing equal 300 ms windows.
   bool valid=true;
   for(int sample=0;sample<30;sample++){
    uint32_t readings[5];for(auto& v:readings)v=analogReadMilliVolts(Config::VOLTAGE_PIN);
    float volts=sourceVolts(medianFive(readings));
    startupPower.lastVolts=volts;
    if(!isfinite(volts)||volts<3||volts>6){valid=false;startupPower.failure=2;startupPower.result="invalid divider reading";break;}
    startupPower.stats[level].add(volts);
    if(volts>StartupPower::OVERVOLTAGE){valid=false;startupPower.failure=5;startupPower.result="voltage above 5.5 V";break;}
    delay(10);
   }
   startupPower.tested=level+1;
   accepted=valid&&startupPower.accept(level);
   if(accepted||startupPower.failure==2||startupPower.failure==5)break;
   // Remove a questionable load before one fresh confirmation attempt.
   pixels.clear();pixels.show();delay(300);
  }
  if(!accepted)break;
 }
 operatingTotal=startupPower.maximum;startupResult=startupPower.result;
 if(computerUsbMode&&!startupPower.failure&&operatingTotal==400)startupResult="computer USB cap";
 // Immediately remove the rejected load; hold the accepted indicator for two seconds.
 pixels.clear();pixels.show();
 if(startupPower.failure)saveStartupFailure();
 if(operatingTotal){
  uint8_t accepted=0;while(accepted<StartupPower::LEVEL_COUNT-1&&StartupPower::levels[accepted]!=operatingTotal)accepted++;
  startupPower.pattern(frame,accepted,wiring);showFrame();delay(2000);
 }
 pixels.clear();pixels.show();setBrightness(100);touchGain=0;
 ambientGain=autoLight?ambient.targetGain():100;
 printPowerStats();
}

bool readTouchPressed(uint32_t now,int& event) {
#if DRAGON_USE_TTP223
 static bool pressed=false,candidate=false;static uint32_t changed=0;
 bool next=digitalRead(Config::TOUCH_PIN)!=0;
 if(next!=candidate){candidate=next;changed=now;}
 event=0;if(candidate!=pressed&&uint32_t(now-changed)>=Config::TOUCH_DEBOUNCE_MS){pressed=candidate;event=pressed?1:-1;}
 return pressed;
#else
 event=nativeTouch.update(touchRead(Config::TOUCH_PIN),now);return nativeTouch.pressed;
#endif
}
void updateTouch(uint32_t now) {
 if(!sunrise.active&&!DragonLibrary::contains(library.data,library.next(255),library.data.active))return;
 if(setupRequested){
  // Consume the setup hold; releasing it must not change brightness or dragon.
  if(digitalRead(Config::TOUCH_PIN)==0){setupRequested=false;gestures=TouchGestures{};}
  return;
 }
 if(uint32_t(now-lastTouch)<Config::TOUCH_SAMPLE_MS)return;lastTouch=now;
#if DRAGON_USE_TTP223
 bool pressed=digitalRead(Config::TOUCH_PIN)!=0;
#else
 int event=0;bool pressed=readTouchPressed(now,event);
#endif
 bool wasPressed=gestures.pressed;
 auto action=gestures.update(pressed,now);
 if(action!=TouchGestures::NONE&&sunrise.active){sunrise.stop();return;}
 if(!wasPressed&&gestures.pressed)touchPresses++;
 switch(action){
  case TouchGestures::SINGLE:{
   bool off=mode==OFF||brightness==0;
   if(off)wakeLighting();else{setPalette(library.next(palette));mode=ZONE_VIEW;}
   Serial.println("Touch: single");break;
  }
  case TouchGestures::DOUBLE:toggleLighting();Serial.println("Touch: double");break;
  case TouchGestures::HOLD_START:
   if(mode==OFF||brightness==0){wakeLighting();dimUp=true;}
   // Fall through for the first dim step.
  case TouchGestures::HOLD_STEP:
   if(dimUp&&brightness<100)setBrightness(brightness+10);
   if(!dimUp&&brightness>10)setBrightness(brightness-10);
   break;
  case TouchGestures::HOLD_END:dimUp=!dimUp;Serial.println("Touch: hold");break;
  default:break;
 }
}

bool readNumber(char* s,int low,int high,int& result){if(!s||!*s)return false;char* end=nullptr;long v=strtol(s,&end,10);if(*end||v<low||v>high)return false;result=int(v);return true;}
void printSensors(){
 Serial.printf("uptime_ms=%lu session_max=%umA computer_usb_cap=%u voltage_sampling=stopped\n",(unsigned long)millis(),operatingTotal,computerUsbMode);
 Serial.printf("sensors touch=%d presses=%lu ldr=%u filtered=%.0f night=%u auto=%u light_step=%u light_gain=%u touch_step=%u touch_gain=%u thresholds=%u/%u calibrated=%u\n",
 digitalRead(Config::TOUCH_PIN),(unsigned long)touchPresses,ambient.raw,ambient.filtered,ambient.night,autoLight,ambient.step,ambientGain,brightness/10,touchGain,ambient.dark,ambient.bright,lightCalibrated);
}
void printStatus() {
 printSensors();
 unsigned customCount=0;for(const auto& c:library.data.customs)customCount+=c.used!=0;
 Serial.printf("library_ready=%u profile=%u profile_name=%s customs=%u generation=%lu\n",library.isReady(),library.data.active,library.data.profiles[library.data.active].name,customCount,(unsigned long)library.data.generation);
 Serial.printf("dragon=%s name=%s effects=%u presets=%u mode=%u estimate=%umA result=%s\n",currentPreset.id,currentPreset.name,currentPreset.effects,PRESET_COUNT,unsigned(mode),estimatedMa+runtimeReserve(operatingTotal),startupResult);
}
void printHelp() {
 Serial.println("Dragon: tap=next/wake, double tap=on/off, hold=brightness. Touch preserves automatic light adjustment.");
 Serial.println("sensors | auto on|off | light DARK BRIGHT (0..4095)");
 Serial.println("light calibrate COVERED UNCOVERED (stable readings; saved across restarts)");
 Serial.println("mode zones|breathe|colorcycle|glitter|incendio|leviosa|solid|corners|chase|off");
 Serial.printf("brightness 0 or 10..100 (ten steps) | palette 0..%u | dragon ID | dragons | color R G B | power status | status | help\n",PRESET_COUNT-1);
}
void handleCommand(char* line) {
 if(networkSerialCommand(line))return;
 char* args[8];int n=0;char* ctx=nullptr;
 for(char* t=strtok_r(line," \t",&ctx);t;t=strtok_r(nullptr," \t",&ctx)){if(n==8){Serial.println("Too many arguments");return;}args[n++]=t;}
 if(!n)return;int a,b,c;bool ok=false;
 if(n==2&&!strcmp(args[0],"alarm")){
  if(!strcmp(args[1],"preview"))sunrise.startPreview(millis());
  else if(!strcmp(args[1],"stop"))sunrise.stop();
  else if(!strcmp(args[1],"disable")){
   auto value=sunrise.settings;value.enabled=false;
   if(!saveAlarmSettings(value)){Serial.println("Alarm disable failed: settings were not saved.");return;}
  }
  else if(strcmp(args[1],"status")){Serial.println("Alarm command: preview, stop, disable or status.");return;}
  Serial.printf("alarm_status active=%u preview=%u progress=%u clock_ready=%u enabled=%u\n",
   sunrise.active,sunrise.preview,sunrise.level/10,DragonAlarm::clockReady(sunrise.settings,alarmEpoch()),sunrise.settings.enabled);
  return;
 }
 if(n==1&&!strcmp(args[0],"sensors")){printSensors();return;}
 if(n==2&&!strcmp(args[0],"auto")&&(!strcmp(args[1],"on")||!strcmp(args[1],"off"))){
  bool enable=!strcmp(args[1],"on");
  if(enable){if(mode==OFF||brightness==0)wakeLighting();rememberLighting();autoLight=true;}
  else manualControl();
  Serial.println("OK");return;
 }
 if(n==3&&!strcmp(args[0],"light")&&readNumber(args[1],0,4094,a)&&readNumber(args[2],1,4095,b)&&a<b){
  Serial.println(saveLightSettings(a,b)?"Light thresholds saved":"Light settings save failed");return;
 }
 if(n==4&&!strcmp(args[0],"light")&&!strcmp(args[1],"calibrate")&&readNumber(args[2],0,4095,a)&&readNumber(args[3],0,4095,b)){
  AmbientLight candidate=ambient;
  if(!candidate.calibrate(a,b)){Serial.println("Calibration needs uncovered >= covered + 200; check wiring/light exposure.");return;}
  Serial.println(saveLightSettings(candidate.dark,candidate.bright)?"Light calibration saved":"Light settings save failed");return;
 }
 if(n==1&&!strcmp(args[0],"dragons")){
  for(int i=0;i<PRESET_COUNT;i++)if(!PRESET_RETIRED[i])Serial.printf("%u %s - %s\n",i,DRAGON_PRESETS[i].id,DRAGON_PRESETS[i].name);
  return;
 }
 if(!strcmp(args[0],"help")){printHelp();return;}
 if(n==2&&!strcmp(args[0],"power")&&!strcmp(args[1],"status")){printPowerStats();return;}
 if(n==1&&!strcmp(args[0],"status")){printStatus();return;}
 if(n==2&&!strcmp(args[0],"brightness")&&readNumber(args[1],0,100,a)){setBrightness(a);ok=true;}
 else if(n==2&&!strcmp(args[0],"palette")&&readNumber(args[1],0,PRESET_COUNT-1,a)){setPalette(a);mode=ZONE_VIEW;ok=true;}
 else if(n==2&&!strcmp(args[0],"dragon")){
  for(int i=0;i<PRESET_COUNT;i++)if(!PRESET_RETIRED[i]&&!strcmp(args[1],DRAGON_PRESETS[i].id)){setPalette(i);mode=ZONE_VIEW;ok=true;break;}
 }
 else if(n==4&&!strcmp(args[0],"color")&&readNumber(args[1],0,255,a)&&readNumber(args[2],0,255,b)&&readNumber(args[3],0,255,c)){solidColor={uint8_t(a),uint8_t(b),uint8_t(c)};mode=SOLID;ok=true;}
 else if(n==2&&!strcmp(args[0],"mode")){
  const char* names[]={"zones","breathe","colorcycle","glitter","incendio","leviosa","solid","corners","chase","off"};
  for(int i=0;i<10;i++)if(!strcmp(args[1],names[i])){if(i==OFF)rememberLighting();mode=Mode(i);ok=true;}
 }
 Serial.println(ok?"OK":"Invalid command; type help");
}
void readSerial() {
 for(int count=0;count<128&&Serial.available();count++){
  char ch=Serial.read();if(ch=='\r')continue;
  if(ch=='\n'){
   if(lineOverflow)Serial.println("Command too long; discarded");
   else{commandLine[commandLength]=0;handleCommand(commandLine);}
   commandLength=0;lineOverflow=false;
  }else if(!lineOverflow){if(commandLength<sizeof(commandLine)-1)commandLine[commandLength++]=ch;else lineOverflow=true;}
 }
}

#ifdef ARDUINO
#include "DragonWeb.h"
bool networkSerialCommand(char* line){return DragonWeb::serialControl(line);}
#else
// Host lighting tests have no radio; connection policy is tested separately.
namespace DragonWeb { constexpr bool ap=false; void begin(bool){} void update(uint32_t){} }
bool networkSerialCommand(char*){return false;}
#endif

void setup() {
 Serial.begin(115200);pixels.begin();pixels.clear();pixels.show();
#if DRAGON_USE_TTP223
 pinMode(Config::TOUCH_PIN,INPUT_PULLDOWN);
#else
 nativeTouch.reset();
#endif
 analogReadResolution(12);analogSetPinAttenuation(Config::LIGHT_PIN,ADC_11db);
 analogSetPinAttenuation(Config::VOLTAGE_PIN,ADC_11db);
 loadSavedFailure();
 loadLightSettings();
 loadAlarmSettings();
 library.begin();
 for(int i=0;i<ZONE_COUNT;i++)zoneGain[i]=100;for(int i=0;i<64;i++)pixelGain[i]=100;
 // Calibrate once per boot; ambient and touch percentages are session-local.
 setPalette(DEFAULT_PRESET);delay(250);printHelp();
 ambient.update(analogRead(Config::LIGHT_PIN),millis());startupCheck();
 const auto& profile=library.data.profiles[library.data.active];
 setPalette(library.next(255));mode=DragonLibrary::contains(library.data,palette,library.data.active)?ZONE_VIEW:OFF;setBrightness(profile.brightness);rememberLighting();
 if(networkBudgetAvailable(operatingTotal))DragonWeb::begin(setupRequested);
 else if(operatingTotal)Serial.println("Touch-only power fallback: Wi-Fi remains off at this session ceiling.");
 if(DragonWeb::ap&&operatingTotal){
  clear(frame);frame[logicalIndex(3,2,wiring)]={8,0,8};showFrame();delay(700);
 }
}
void loop() {
 readSerial();DragonWeb::update(millis());
 uint32_t now=millis();
 sunrise.update(alarmEpoch(),now);
 // Once a computer is seen, keep the conservative ceiling until the next boot.
 if(!computerUsbMode&&uint32_t(now-lastUsbCheck)>=250){
  lastUsbCheck=now;
  if(computerUsbConnected()){
   computerUsbMode=true;
   if(operatingTotal>400){operatingTotal=400;startupResult="computer USB cap";}
  }
 }
 updateTouch(now);updateLight(now);render(now);
 if(telemetry&&uint32_t(now-lastReport)>=2000){lastReport=now;if(Serial)printStatus();}
 delay(1);
}
