#define CONFIG_IDF_TARGET_ESP32S3 1
#include "../DragonPrototype/DragonPrototype.ino"
#include <cassert>
using DragonAlarm::Alarm;
using DragonAlarm::Settings;
Settings config(uint16_t minute=7*60,uint16_t duration=20){
 Settings s{};s.enabled=1;s.minute=minute;s.duration=duration;
 s.validFrom=1704067200;s.validUntil=s.validFrom+400u*86400u;
 return s;
}
int main(){
 const int64_t day=1704153600; // UTC midnight, 2 Jan 2024; phone clock is injected.
 Alarm a;a.apply(config());
 a.update(day+6*3600,0);assert(!a.active);
 a.update(day+6*3600+40*60,1000);assert(a.active&&a.level==1);
 a.update(day+6*3600+50*60,601000);assert(a.level>=499&&a.level<=501);
 a.update(day+7*3600,1201000);assert(a.level==1000);
 a.stop();a.update(day+7*3600,1202000);assert(!a.active); // no repeat today
 a.update(day+86400+6*3600+40*60,1203000);assert(a.active); // daily repeat
 a.update(day+86400+8*3600,4203000);assert(!a.active); // hold expires
 a.update(day+86400+7*3600,4204000);assert(!a.active); // backward clock cannot retrigger
 a.apply(config(10,30));a.update(day-10*60,0);assert(a.active); // midnight crossover
 a.stop();a.update(day-9*60,1000);assert(!a.active);
 Alarm offline;offline.apply(config());offline.update(0,1000);assert(!offline.active);
 offline.startPreview(0xfffffff0u);offline.update(0,uint32_t(0xfffffff0u+15000));
 assert(offline.active&&offline.preview&&offline.level>490&&offline.level<510);
 offline.update(0,uint32_t(0xfffffff0u+40000));assert(!offline.active);
 // Saved phone rules advance the local alarm automatically across DST.
 Settings dst=config(7*60,20);dst.offset=60;dst.count=1;
 dst.changes[0].at=uint32_t(day+86400+3600);dst.changes[0].offset=120;
 Alarm summer;summer.apply(dst);
 summer.update(day+86400+4*3600+40*60,0);assert(summer.active); // 06:40 local +02
 // A skipped spring clock time does not invent an alarm at another wall time.
 dst.minute=2*60+30;Alarm skipped;skipped.apply(dst);
 skipped.update(day+86400+3600,0);assert(!skipped.active);
 // Fall-back repeated wall times only trigger once per local day.
 dst.minute=2*60+30;dst.offset=120;dst.changes[0].offset=60;
 Alarm fall;fall.apply(dst);fall.update(day+86400+30*60,0);assert(fall.active);
 fall.stop();fall.update(day+86400+90*60,1000);assert(!fall.active);
 // Persistence uses a separate record and rejects invalid/corrupted settings.
 auto settings=config();assert(saveAlarmSettings(settings));sunrise=Alarm{};loadAlarmSettings();assert(sunrise.settings.enabled);
 auto saved=sunrise.settings;failStore=true;settings.minute=480;assert(!saveAlarmSettings(settings));assert(sunrise.settings.minute==saved.minute);failStore=false;
 otherPreferences["dragon-alarm/settings"][0]^=1;sunrise=Alarm{};loadAlarmSettings();assert(!sunrise.settings.enabled);
 // Sunrise lights only wings/edges, wakes from manual sleep, and obeys every power ceiling.
 mode=OFF;brightness=0;touchGain=ambientGain=0;
 for(auto budget:StartupPower::levels){
  operatingTotal=budget;startupPower.failure=0;sunrise=Alarm{};sunrise.startPreview(0);
  for(uint32_t t=0;t<=30000;t+=500){
   sunrise.update(0,t);composeFrame(t);assert(estimatedMa+runtimeReserve(budget)<=budget);
   for(int y=0;y<8;y++)for(int x=0;x<8;x++){
    auto pixel=frame[logicalIndex(x,y,wiring)];auto z=ZONES[y][x];
    // Independent body exclusion catches missing former-background wing pixels.
    bool excluded=z==TAIL||z==BODY||z==FACE||z==LH||z==RH;
    if(excluded)assert(pixel.r+pixel.g+pixel.b==0);
    else if(t==30000&&budget>=400)assert(pixel.r+pixel.g+pixel.b>0);
    assert(pixel.r<=204&&pixel.g<=204&&pixel.b<=204);
   }
  }
  if(budget>=400)assert(channelSum(frame)>0);
 }
 toggleLighting();assert(!sunrise.active&&mode==OFF&&brightness==0);composeFrame(31000);assert(channelSum(frame)==0);
 sunrise.startPreview(0);setBrightness(40);assert(!sunrise.active);
 char previewCommand[]="alarm preview";handleCommand(previewCommand);assert(sunrise.active&&sunrise.preview);
 char stopCommand[]="alarm stop";handleCommand(stopCommand);assert(!sunrise.active);
 auto invalid=config();invalid.duration=0;assert(!DragonAlarm::valid(invalid));invalid=config();invalid.count=5;assert(!DragonAlarm::valid(invalid));
 puts("PASS: daily/midnight/DST sunrise, clock loss, preview rollover, cancellation, persistence and all current ceilings.");
}
