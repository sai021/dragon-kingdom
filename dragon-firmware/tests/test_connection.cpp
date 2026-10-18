#include "../DragonPrototype/ConnectionPolicy.h"
#include <cassert>
#include <cstdio>
using namespace DragonConnection;
int main(){
 assert(deviceSuffix(0xb0577372da90ULL)==0xb05773);
 assert(deviceSuffix(0xb0577472da90ULL)!=deviceSuffix(0xb0577372da90ULL));
 assert(openAtBoot(false,false));assert(openAtBoot(false,true));
 assert(!openAtBoot(true,false));assert(openAtBoot(true,true));
 assert(!closeAccessPoint(false,false,0,600000,0));
 assert(!closeAccessPoint(true,true,0,600000,0));
 assert(!closeAccessPoint(true,false,1,600000,0));
 assert(!closeAccessPoint(true,false,0,299999,0));
 assert(closeAccessPoint(true,false,0,300000,0));
 assert(elapsed(100,UINT32_MAX-99,200));
 assert(!elapsed(45000,0,CONNECT_TIMEOUT_MS)); // permit the observed slow DHCP path
 assert(!elapsed(1000,1001,CONNECT_TIMEOUT_MS)); // request started after caller's clock sample
 assert(!closeAccessPoint(true,false,0,1000,1001)); // freshly reopened AP stays visible
 assert(elapsed(60000,0,CONNECT_TIMEOUT_MS));
 assert(elapsed(59900,UINT32_MAX-99,CONNECT_TIMEOUT_MS));
 assert(joinedExpectedNetwork(true,false,true,true)); // late DHCP must still save
 assert(!joinedExpectedNetwork(true,true,true,false)); // old network must not save new key
 assert(joinedExpectedNetwork(true,true,false,false)); // reconnect saved network
 assert(!joinedExpectedNetwork(true,false,false,false)); // no repeated save/MDNS restart
 assert(!joinedExpectedNetwork(false,true,true,true));
 assert(!elapsed(99,UINT32_MAX-99,200));
 StartupHold hold;
 hold.observe(true,500);hold.observe(true,2499);assert(!hold.requested);
 hold.observe(true,2500);assert(hold.requested);
 hold.observe(false,3000);assert(hold.requested); // stays latched for startup
 StartupHold ordinary;
 ordinary.observe(false,500);ordinary.observe(true,1000);ordinary.observe(true,4000);
 assert(!ordinary.requested); // a later press cannot become the setup gesture
 StartupHold interrupted;
 interrupted.observe(true,500);interrupted.observe(false,1000);interrupted.observe(true,1500);interrupted.observe(true,4000);
 assert(!interrupted.requested);
 StartupHold rollover;
 rollover.observe(true,UINT32_MAX-999);rollover.observe(true,1000);assert(rollover.requested);
 puts("PASS: first-use setup, deliberate recovery, AP inactivity, startup hold and timer rollover.");
}
