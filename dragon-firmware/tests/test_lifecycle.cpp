#include "../DragonPrototype/BootValidation.h"
#include "../DragonPrototype/CompatibilityPolicy.h"
#include "../DragonPrototype/ConnectionPolicy.h"
#include <cassert>
#include <initializer_list>
#include <cstdio>
int main(){
 using namespace DragonBoot;
 for(bool healthy:{false,true}){Validation v;v.state=State::Valid;assert(v.decide(61000,healthy)==Action::None);}
 Validation t;t.state=State::Trial;assert(t.decide(29000,true)==Action::None);assert(t.decide(30000,true)==Action::Confirm);assert(t.decide(61000,false)==Action::None);
 Validation fail;fail.state=State::Trial;assert(fail.decide(60000,false)==Action::Rollback);assert(fail.decide(60001,false)==Action::None);
 Validation migration;migration.state=State::Migration;assert(migration.decide(60000,false)==Action::None);
 Validation seed;seed.state=State::Migration;assert(seed.decide(30000,true)==Action::SeedAndConfirm);
 Validation unknown;assert(unknown.decide(60000,true)==Action::None);
 using namespace DragonCompatibility;
 for(bool calibrated:{false,true}){assert(compatible(1,1,calibrated));assert(!compatible(1,2,calibrated));assert(compatible(0,1,calibrated)==!calibrated);}
 assert(!allowed("v0.2.0","v0.3.0-beta.4",false));assert(!allowed("v0.3.0-beta.4","v0.3.0-beta.4",false));assert(allowed("v0.3.0","v0.3.0-beta.4",false));assert(allowed("v0.3.1-beta.1","v0.3.0",false));assert(allowed("v0.2.0","v0.3.0",true));assert(!allowed("v0.2.0-beta.1","v0.3.0",true));assert(!allowed("v0.3","v0.3.0",true));
 DragonConnection::Reconnect reconnect;assert(!reconnect.due(300000,false));reconnect.lost(100);assert(!reconnect.due(10099,false));assert(reconnect.due(10100,false));assert(!reconnect.due(10100,true));
 for(unsigned i=0;i<20;i++)reconnect.failed(200);assert(reconnect.backoff()==300000);assert(reconnect.due(300200,false));reconnect.joined();assert(!reconnect.waiting&&reconnect.failures==0);
 reconnect.lost(UINT32_MAX-5000);assert(reconnect.due(5000,false));
 puts("PASS: boot validation, signed compatibility decisions and bounded station reconnect policy (no ESP driver/bootloader).");
}
