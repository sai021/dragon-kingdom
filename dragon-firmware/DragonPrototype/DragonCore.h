#pragma once
#include <stdint.h>
#include <stddef.h>
#include "Config.h"
namespace Dragon {
constexpr int PHYSICAL_WIDTH = Config::MATRIX_WIDTH, PHYSICAL_COUNT = Config::MATRIX_COUNT, LOGICAL_WIDTH = 8;
struct RGB { uint8_t r, g, b; };
// BG retains its stored ID for compatibility; every physical pixel is now a body part or wing.
enum Zone : uint8_t { BG, LE, RE, LH, RH, FACE, BODY, TAIL, LW, RW, ZONE_COUNT };
static const char* const ZONE_NAMES[] = {"BG","LE","RE","LH","RH","FACE","BODY","TAIL","LW","RW"};
static const Zone ZONES[8][8] = {
 {LW,LE,LE,LW,RW,RE,RE,RW},
 {LE,LW,LH,FACE,FACE,RH,RW,RE},
 {LE,LW,FACE,FACE,FACE,FACE,RW,RE},
 {LW,LW,FACE,FACE,FACE,FACE,RW,RW},
 {LW,LW,LW,BODY,BODY,RW,RW,RW},
 {LW,LW,BODY,BODY,BODY,BODY,RW,RW},
 {LW,TAIL,BODY,BODY,BODY,BODY,RW,RW},
 {LW,TAIL,TAIL,TAIL,TAIL,RW,RW,RW}
};
struct Wiring {
 bool serpentine = true;
 bool columns = false;
 // Front-facing view: correct the observed left/right reversal on the matrix.
 bool mirror = true;
 uint8_t quarterTurns = 0;
 uint8_t offsetX = 0, offsetY = 0;
};
inline int physicalIndex(int x, int y, const Wiring& w) {
 if(x<0 || x>=PHYSICAL_WIDTH || y<0 || y>=PHYSICAL_WIDTH) return -1;
 if(w.mirror) x=PHYSICAL_WIDTH-1-x;
 for(uint8_t r=0;r<(w.quarterTurns%4);++r) { int old=x; x=PHYSICAL_WIDTH-1-y; y=old; }
 int major=w.columns?x:y, minor=w.columns?y:x;
 if(w.serpentine && (major&1)) minor=PHYSICAL_WIDTH-1-minor;
 return major*PHYSICAL_WIDTH+minor;
}
inline int logicalIndex(int x,int y,const Wiring& w) {
 if(x<0||x>=8||y<0||y>=8||w.offsetX>PHYSICAL_WIDTH-LOGICAL_WIDTH||w.offsetY>PHYSICAL_WIDTH-LOGICAL_WIDTH) return -1;
 return physicalIndex(x+w.offsetX,y+w.offsetY,w);
}
inline uint8_t clampByte(uint32_t n) { return n>255?255:static_cast<uint8_t>(n); }
inline RGB scaled(RGB c, uint32_t numerator, uint32_t denominator) {
 return {clampByte(uint32_t(c.r)*numerator/denominator),clampByte(uint32_t(c.g)*numerator/denominator),clampByte(uint32_t(c.b)*numerator/denominator)};
}
inline void clear(RGB* f) {for(int i=0;i<PHYSICAL_COUNT;i++)f[i]={0,0,0};}
inline uint32_t channelSum(const RGB* f) {uint32_t s=0;for(int i=0;i<PHYSICAL_COUNT;i++)s+=f[i].r+f[i].g+f[i].b;return s;}
inline uint16_t estimatedMilliAmps(const RGB* f) {return Config::PANEL_IDLE_MA+(channelSum(f)*20+254)/255;}
inline void capCurrent(RGB* f,uint16_t budget) {
 // Conservative illustrative model: 1 mA idle per physical LED plus 20 mA/channel.
 const uint32_t available=budget>Config::PANEL_IDLE_MA?budget-Config::PANEL_IDLE_MA:0;
 const uint32_t allowed=available*255/20, sum=channelSum(f);
 if(sum>allowed && sum)for(int i=0;i<PHYSICAL_COUNT;i++)f[i]=scaled(f[i],allowed,sum);
}
inline float sourceVolts(float adcMv) {
 return adcMv*.001f*(Config::DIVIDER_HIGH_OHMS+Config::DIVIDER_LOW_OHMS)/Config::DIVIDER_LOW_OHMS*Config::VOLTAGE_CALIBRATION;
}
struct TouchFilter {
 float baseline=0;
 uint32_t raw=0, candidateSince=0, samples=0;
 uint64_t calibrationSum=0;
 bool ready=false, pressed=false, candidate=false;
 void reset() {baseline=0;raw=0;candidateSince=0;samples=0;calibrationSum=0;ready=false;pressed=false;candidate=false;}
 // Returns +1 on debounced press, -1 on release, zero otherwise.
 int update(uint32_t value,uint32_t now) {
  raw=value;
  if(!value) { reset(); return 0; } // invalid readings disarm touch until recalibrated
  if(!ready) {calibrationSum+=value;if(++samples>=64){baseline=float(calibrationSum)/samples;ready=true;}return 0;}
  bool next=pressed ? value>baseline*Config::TOUCH_OFF_RATIO : value>baseline*Config::TOUCH_ON_RATIO;
  if(next!=candidate){candidate=next;candidateSince=now;}
  int event=0;
  if(candidate!=pressed && uint32_t(now-candidateSince)>=Config::TOUCH_DEBOUNCE_MS){pressed=candidate;event=pressed?1:-1;}
  // Never adapt toward a touch; gently track ordinary untouched drift.
  if(!pressed&&!candidate&&value<baseline*Config::TOUCH_OFF_RATIO) baseline+=.005f*(float(value)-baseline);
  return event;
 }
};
}
