#pragma once
#include <stdint.h>

namespace DragonConnection {
// Real association retries plus DHCP on the test network exceeded 20 seconds.
constexpr uint32_t CONNECT_TIMEOUT_MS=60000;
constexpr uint32_t RETRY_MS=60000;
constexpr uint32_t AP_IDLE_MS=300000;
// ESP eFuse returns MAC bytes in little-endian order. Skip the vendor prefix.
inline uint32_t deviceSuffix(uint64_t efuseMac){return uint32_t(efuseMac>>24)&0xffffff;}
inline bool elapsed(uint32_t now,uint32_t since,uint32_t interval){
 // These short deadlines are checked continuously. A timer set by a request
 // after the caller sampled now is still in the future, not overdue.
 uint32_t delta=uint32_t(now-since);
 return delta<0x80000000u&&delta>=interval;
}
inline bool joinedExpectedNetwork(bool online,bool connecting,bool pending,bool matches){
 // A slow driver/DHCP completion can arrive after the UI deadline.
 // Only commit a pending candidate if the actual network matches it.
 return online&&(pending?matches:connecting);
}
inline bool openAtBoot(bool configured,bool requested){return !configured||requested;}
inline bool closeAccessPoint(bool configured,bool connecting,unsigned clients,uint32_t now,uint32_t activity){
 return configured&&!connecting&&!clients&&elapsed(now,activity,AP_IDLE_MS);
}
struct StartupHold {
 bool released=false,tracking=false,requested=false;
 uint32_t since=0;
 void observe(bool pressed,uint32_t now){
  if(!pressed){released=true;tracking=false;return;}
  if(released)return;
  if(!tracking){since=now;tracking=true;}
  if(elapsed(now,since,2000))requested=true;
 }
};
}
