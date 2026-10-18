#pragma once
#include <stdint.h>
#include <stddef.h>
#include <math.h>

namespace Dragon {
inline uint32_t medianFive(uint32_t (&values)[5]){
 for(int i=1;i<5;i++)for(int j=i;j>0&&values[j]<values[j-1];j--){
  uint32_t swap=values[j];values[j]=values[j-1];values[j-1]=swap;
 }
 return values[2];
}
// 3V3 -> LDR -> ADC -> 10k -> GND: larger readings mean more light.
struct AmbientLight {
 uint16_t dark=600, bright=3400, raw=0;
 float filtered=0;
 bool ready=false, night=true, candidate=true;
 uint32_t candidateSince=0,stepSince=0;
 uint8_t step=1,stepCandidate=1;
 void update(uint16_t value,uint32_t now) {
  raw=value;
  if(!ready){filtered=value;ready=true;candidateSince=now;}
  else filtered+=(value-filtered)*0.25f;
  uint16_t restoreThreshold=bright>200?bright-200:bright;
  bool next=night;
  if(filtered>bright)next=false;
  else if(filtered<restoreThreshold)next=true;
  if(next!=candidate){candidate=next;candidateSince=now;}
  if(candidate!=night&&uint32_t(now-candidateSince)>=5000)night=candidate;
  uint8_t nextStep=1;
  if(filtered>dark&&bright>dark){
   uint32_t span=bright-dark;
   uint32_t rel=uint32_t(filtered-dark);
   nextStep=1+(rel*9)/span;
   if(nextStep>10)nextStep=10;
  }
  // 24 ADC counts of hysteresis around each bin, plus one-second dwell.
  if(bright>dark){
   float binWidth=float(bright-dark)/9.0f;
   if(nextStep>step&&filtered<float(dark)+float(step)*binWidth+24)nextStep=step;
   if(nextStep<step&&filtered>float(dark)+float(step-1)*binWidth-24)nextStep=step;
  }
  if(nextStep!=stepCandidate){stepCandidate=nextStep;stepSince=now;}
  if(step!=stepCandidate&&uint32_t(now-stepSince)>=1000)step=stepCandidate;
 }
 uint8_t targetGain() const {
  if(!ready)return 100;
  // Bright daylight should look awake, not switch the dragon off.
  if(!night)return 100;
  return step*10;
 }
 bool calibrate(uint16_t covered,uint16_t uncovered) {
  if(uncovered>4095||covered>4095||uncovered<covered+200)return false;
  uint32_t span=uncovered-covered;
  dark=covered+span*15/100;
  uint32_t headroom=4095>uncovered?4095-uncovered:0;
  bright=uncovered+headroom*50/100;
  if(bright<uncovered+200)bright=uncovered+200;
  if(bright>4000)bright=4000;
  candidate=night;
  return true;
 }
};

struct TouchGestures {
 bool pressed=false,candidate=false,held=false,pending=false;
 uint32_t changed=0,started=0,released=0,lastStep=0;
 enum Action { NONE, SINGLE, DOUBLE, HOLD_START, HOLD_STEP, HOLD_END };
 Action update(bool down,uint32_t now) {
  if(down!=candidate){candidate=down;changed=now;}
  if(candidate!=pressed&&uint32_t(now-changed)>=50){
   pressed=candidate;
   if(pressed){started=now;lastStep=now;held=false;}
   else if(held){held=false;return HOLD_END;}
   else {
    if(pending&&uint32_t(now-released)<=400){pending=false;return DOUBLE;}
    pending=true;released=now;
   }
  }
  if(pressed&&uint32_t(now-started)>=700){
   pending=false;
   if(!held){held=true;lastStep=now;return HOLD_START;}
   if(uint32_t(now-lastStep)>=400){lastStep=now;return HOLD_STEP;}
  }
  if(pending&&!pressed&&!candidate&&uint32_t(now-released)>400){pending=false;return SINGLE;}
  return NONE;
 }
};

}
