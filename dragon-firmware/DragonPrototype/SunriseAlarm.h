#pragma once
#include <stdint.h>
#include <stddef.h>

namespace DragonAlarm {
constexpr uint32_t MAGIC=0x53554e31u;
constexpr uint32_t HOLD_SECONDS=30*60;
constexpr uint8_t TRANSITIONS=4;
struct Transition {uint32_t at=0;int16_t offset=0;uint16_t reserved=0;};
// Clock rules come from the phone's actual timezone, including future DST changes.
// A separate namespace/record leaves all existing library and Wi-Fi data intact.
struct Settings {
 uint32_t magic=MAGIC,validFrom=0,validUntil=0;
 uint16_t minute=7*60,duration=20;
 int16_t offset=0;
 uint8_t enabled=0,count=0;
 Transition changes[TRANSITIONS]{};
 uint32_t check=0;
};
static_assert(sizeof(Settings)==56,"Alarm record must have a stable layout.");
inline bool validOffset(int offset){return offset>=-14*60&&offset<=14*60;}
inline bool valid(const Settings& s){
 if(s.magic!=MAGIC||s.enabled>1||s.minute>=1440||s.duration<1||s.duration>120||
    !validOffset(s.offset)||s.count>TRANSITIONS)return false;
 if(s.validFrom<1704067200u||s.validUntil<=s.validFrom||s.validUntil>4102444800u||
    s.validUntil-s.validFrom>402u*86400u)return false;
 uint32_t previous=s.validFrom;
 for(uint8_t i=0;i<s.count;i++){
  if(s.changes[i].at<=previous||s.changes[i].at>=s.validUntil||
     !validOffset(s.changes[i].offset)||s.changes[i].reserved)return false;
  previous=s.changes[i].at;
 }
 return true;
}
inline uint32_t checksum(const Settings& s){
 uint32_t hash=2166136261u;
 const auto* bytes=reinterpret_cast<const uint8_t*>(&s);
 for(size_t i=0;i<offsetof(Settings,check);i++)hash=(hash^bytes[i])*16777619u;
 return hash;
}
inline bool clockReady(const Settings& s,int64_t epoch){return epoch>=s.validFrom&&epoch<s.validUntil&&s.validFrom!=0;}
inline int offsetAt(const Settings& s,int64_t epoch){
 int offset=s.offset;for(uint8_t i=0;i<s.count&&epoch>=s.changes[i].at;i++)offset=s.changes[i].offset;
 return offset;
}
struct Alarm {
 Settings settings{};
 int64_t day=-1,dismissed=-1;
 uint32_t started=0,initialSeconds=0;
 bool active=false,preview=false;
 uint16_t level=0; // 0..1000, independently of manual sleep/ambient dimming.
 void stop(){if(active&&!preview&&day>dismissed)dismissed=day;active=preview=false;level=0;}
 void apply(const Settings& value){stop();settings=value;dismissed=-1;}
 void startPreview(uint32_t now){stop();active=preview=true;started=now;initialSeconds=0;level=1;}
 void update(int64_t epoch,uint32_t now){
  if(!active&&settings.enabled&&clockReady(settings,epoch)){
   int64_t today=(epoch+offsetAt(settings,epoch)*60)/86400;
   int64_t selected=INT64_MAX,selectedDay=-1;
   for(int delta=-1;delta<=1;delta++)for(uint8_t i=0;i<=settings.count;i++){
    int64_t candidateDay=today+delta;
    int offset=i?settings.changes[i-1].offset:settings.offset;
    int64_t target=candidateDay*86400+settings.minute*60-offset*60;
    if(candidateDay<=dismissed||offsetAt(settings,target)!=offset||!clockReady(settings,target))continue;
    int64_t start=target-settings.duration*60;
    if(epoch>=start&&epoch<target+HOLD_SECONDS&&target<selected){selected=target;selectedDay=candidateDay;}
   }
   if(selectedDay>=0){active=true;preview=false;day=selectedDay;started=now;
    initialSeconds=uint32_t(epoch-(selected-settings.duration*60));}
  }
  if(!active)return;
  uint32_t durationMs=preview?30000u:uint32_t(settings.duration)*60000u;
  uint64_t elapsed=uint64_t(uint32_t(now-started))+uint64_t(initialSeconds)*1000;
  if(elapsed>=uint64_t(durationMs)+(preview?10000u:HOLD_SECONDS*1000u)){stop();return;}
  // Smoothstep, with a tiny initial glow; the normal current cap still applies.
  float progress=elapsed>=durationMs?1.0f:float(elapsed)/durationMs;
  level=uint16_t(1+999*progress*progress*(3-2*progress));
 }
};
}
