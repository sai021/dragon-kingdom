#pragma once
#include "DragonCore.h"

namespace Dragon {
constexpr uint16_t BASE_TOTAL_MA=Config::PANEL_IDLE_MA+Config::ESP_RESERVE_MA;
constexpr uint16_t MIN_TOTAL_MA=Config::MIN_TOTAL_MA;
constexpr uint16_t MAX_TOTAL_MA=Config::DEFAULT_MAX_TOTAL_MA;

inline bool networkBudgetAvailable(uint16_t ceiling){return ceiling>=BASE_TOTAL_MA+Config::WIFI_RESERVE_MA;}
inline uint16_t runtimeReserve(uint16_t ceiling){return Config::ESP_RESERVE_MA+(networkBudgetAvailable(ceiling)?Config::WIFI_RESERVE_MA:0);}

inline RGB visibleScale(RGB c,uint32_t numerator,uint32_t denominator) {
 // Nearest rounding avoids consistently discarding weaker components.
 RGB out={clampByte((uint32_t(c.r)*numerator+denominator/2)/denominator),
          clampByte((uint32_t(c.g)*numerator+denominator/2)/denominator),
          clampByte((uint32_t(c.b)*numerator+denominator/2)/denominator)};
 if(!numerator)return out;
 uint8_t peak=c.r>c.g?c.r:c.g;if(c.b>peak)peak=c.b;
 // At the one-count floor, quantise the normalised colour symmetrically.
 // A channel at least half the peak is significant. Keep it visible even
 // before its rounded scale reaches one: white stays RGB, yellow stays RG.
 // Applying the fixed mask at every positive gain also keeps each channel
 // monotonic, which the session current-limit binary search requires.
 uint16_t threshold=(uint16_t(peak)+1)/2;
 if(c.r&&c.r>=threshold&&!out.r)out.r=1;
 if(c.g&&c.g>=threshold&&!out.g)out.g=1;
 if(c.b&&c.b>=threshold&&!out.b)out.b=1;
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
