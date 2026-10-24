#pragma once
#include <stdint.h>

namespace DragonConnection {
// Real association retries plus DHCP on the test network exceeded 20 seconds.
constexpr uint32_t CONNECT_TIMEOUT_MS=60000;
constexpr uint32_t RETRY_MS=60000;
struct Reconnect {
 bool waiting=false;uint8_t failures=0;uint32_t since=0;
 uint32_t backoff()const{return failures>=5?300000u:(10000u<<failures);}
 void lost(uint32_t now){waiting=true;since=now;}
 void failed(uint32_t now){if(failures<5)failures++;lost(now);}
 void joined(){waiting=false;failures=0;}
 bool due(uint32_t now,bool busy)const{return waiting&&!busy&&uint32_t(now-since)<0x80000000u&&uint32_t(now-since)>=backoff();}
};
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
// Every powered session starts with setup available. A successful join closes it
// after a short handover window, irrespective of associated phone count.
constexpr uint32_t HANDOVER_MS=15000;
inline bool openAtBoot(bool,bool){return true;}
inline bool closeAccessPoint(bool joined,bool connecting,unsigned,uint32_t now,uint32_t successAt){
 return joined&&!connecting&&elapsed(now,successAt,HANDOVER_MS);
}
}
