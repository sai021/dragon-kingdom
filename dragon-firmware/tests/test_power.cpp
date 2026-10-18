#include "../DragonPrototype/PowerPolicy.h"
#include <cassert>
#include <cstdio>
using namespace Dragon;
int main(){
 assert(MAX_TOTAL_MA==2400&&BASE_TOTAL_MA==264);
 assert(!networkBudgetAvailable(0)&&!networkBudgetAvailable(300)&&networkBudgetAvailable(400));
 assert(runtimeReserve(300)==200&&runtimeReserve(400)==250);
 RGB f[PHYSICAL_COUNT];
 for(int budget=Config::PANEL_IDLE_MA;budget<=MAX_TOTAL_MA;budget++){
  clear(f);for(int i=0;i<64;i++)f[i]={204,uint8_t(i%205),uint8_t((i*3)%205)};
  capVisibleCurrent(f,budget);assert(estimatedMilliAmps(f)<=budget);
  for(int y=0;y<PHYSICAL_WIDTH;y++)for(int x=0;x<PHYSICAL_WIDTH;x++){
   RGB c=f[y*PHYSICAL_WIDTH+x];
   if(y<8&&x<8&&budget>=Config::PANEL_IDLE_MA+6)assert(c.r||c.g||c.b);
   if(y>=8||x>=8)assert(!(c.r||c.g||c.b));
   assert(c.r<=204&&c.g<=204&&c.b<=204);
  }
 }
 puts("PASS: RGB load limiting across all panel budgets.");
}
