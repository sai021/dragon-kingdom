#pragma once
#include "DragonLibrary.h"
#include "SunriseAlarm.h"
#include "Rotation.h"
namespace DragonBackup {
// Versioned ABI snapshot; S3/C3 use the same fixed-width fields and layout.
// Wi-Fi secrets, parent credentials, tokens, diagnostics and clock epoch excluded.
struct Snapshot {
 uint32_t magic=0x444b4231,version=1;
 DragonLibrary::Data library{};
 DragonAlarm::Settings alarm{};
 DragonRotation::Settings rotation{};
 uint16_t dark=1200,bright=2800;
 uint8_t calibrated=0,reset=0,reserved[2]{};
 uint32_t check=0;
};
inline uint32_t checksum(const Snapshot& s){uint32_t v=2166136261u;auto* p=(const uint8_t*)&s;for(size_t i=0;i<offsetof(Snapshot,check);i++)v=(v^p[i])*16777619u;return v;}
inline bool valid(const Snapshot& s){
 bool emptyAlarm=!s.alarm.enabled&&s.alarm.validFrom==0&&s.alarm.validUntil==0&&s.alarm.minute<1440&&s.alarm.duration>=1&&s.alarm.duration<=120&&s.alarm.count==0;
 return s.magic==0x444b4231&&s.version==1&&s.check==checksum(s)&&s.reset<=1&&s.calibrated<=1&&!s.reserved[0]&&!s.reserved[1]&&s.dark<s.bright&&s.bright<=4095&&DragonLibrary::valid(s.library)&&!strcmp(s.library.profiles[0].name,"All")&&s.library.profiles[0].used&&s.library.profiles[0].count==0&&(emptyAlarm||DragonAlarm::valid(s.alarm))&&DragonRotation::valid(s.rotation);
}
}
