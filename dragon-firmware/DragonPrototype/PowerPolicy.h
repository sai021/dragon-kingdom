#pragma once
#include "DragonCore.h"

namespace Dragon {
constexpr uint16_t BASE_TOTAL_MA=Config::PANEL_IDLE_MA+Config::ESP_RESERVE_MA;
constexpr uint16_t MIN_TOTAL_MA=Config::MIN_TOTAL_MA;
constexpr uint16_t MAX_TOTAL_MA=Config::DEFAULT_MAX_TOTAL_MA;

inline bool networkBudgetAvailable(uint16_t ceiling){return ceiling>=BASE_TOTAL_MA+Config::WIFI_RESERVE_MA;}
inline uint16_t runtimeReserve(uint16_t ceiling){return Config::ESP_RESERVE_MA+(networkBudgetAvailable(ceiling)?Config::WIFI_RESERVE_MA:0);}

inline RGB visibleScale(RGB c,uint32_t numerator,uint32_t denominator) {
 RGB out=scaled(c,numerator,denominator);
 if(numerator&&(c.r||c.g||c.b)&&!(out.r||out.g||out.b)) {
  if(c.r>=c.g&&c.r>=c.b)out.r=1;
  else if(c.g>=c.b)out.g=1;else out.b=1;
 }
 return out;
}
inline void capVisibleCurrent(RGB* f,uint16_t panelBudget) {
 if(estimatedMilliAmps(f)<=panelBudget)return;
 const uint32_t allowed=panelBudget>Config::PANEL_IDLE_MA?
  uint32_t(panelBudget-Config::PANEL_IDLE_MA)*255/20:0;
 uint32_t low=0,high=65535;
 while(low<high) {
  uint32_t mid=(low+high+1)/2,sum=0;
  for(int i=0;i<PHYSICAL_COUNT;i++){
   RGB c=visibleScale(f[i],mid,65535);sum+=c.r+c.g+c.b;
  }
  if(sum<=allowed)low=mid;else high=mid-1;
 }
 for(int i=0;i<PHYSICAL_COUNT;i++)f[i]=visibleScale(f[i],low,65535);
}
}
