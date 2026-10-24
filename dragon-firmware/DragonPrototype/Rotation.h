#pragma once
#include <stdint.h>
namespace DragonRotation {
struct Settings {uint32_t magic=0x44524f31,seconds=300;uint8_t enabled=0,shuffle=0,reserved[2]{};};
inline bool valid(const Settings& s){return s.magic==0x44524f31&&s.seconds>=10&&s.seconds<=86400&&s.enabled<=1&&s.shuffle<=1&&!s.reserved[0]&&!s.reserved[1];}
struct State {
 Settings settings{};uint32_t last=0,sequence=0;bool paused=false;
 void restart(uint32_t now){last=now;}
 bool due(uint32_t now,bool pause){
  if(pause||paused||!settings.enabled){last=now;paused=pause;return false;}
  paused=false;if(uint32_t(now-last)<settings.seconds*1000u)return false;last=now;return true;
 }
};
}
