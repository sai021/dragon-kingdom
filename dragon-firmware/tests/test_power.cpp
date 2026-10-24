#include "../DragonPrototype/PowerPolicy.h"
#include <cassert>
#include <cstdio>
#include <initializer_list>
using namespace Dragon;
int main(){
 assert(MAX_TOTAL_MA==2400&&BASE_TOTAL_MA==264);
 assert(!networkBudgetAvailable(0)&&!networkBudgetAvailable(300)&&networkBudgetAvailable(400));
 assert(runtimeReserve(300)==200&&runtimeReserve(400)==250);
 // Neutral and near-neutral colours remain neutral at the visible floor;
 // primaries do not acquire other channels, and black/zero remain black.
 auto white=visibleScale({20,20,20},1,1000);assert(white.r==1&&white.g==1&&white.b==1);
 auto grey=visibleScale({20,19,18},1,1000);assert(grey.r==1&&grey.g==1&&grey.b==1);
 auto nearWhite=visibleScale({200,190,180},15,1000);assert(nearWhite.r==3&&nearWhite.g==3&&nearWhite.b==3);
 auto red=visibleScale({200,1,0},1,1000);assert(red.r==1&&!red.g&&!red.b);
 auto yellow=visibleScale({20,20,0},1,1000);assert(yellow.r==1&&yellow.g==1&&!yellow.b);
 auto black=visibleScale({0,0,0},1,1000);assert(!black.r&&!black.g&&!black.b);
 auto zero=visibleScale({20,20,20},0,1000);assert(!zero.r&&!zero.g&&!zero.b);
 // RGB permutation symmetry and per-channel monotonicity are required even
 // near the floor; no axis is preferred, and binary-search load cannot dip.
 for(RGB colour:{RGB{255,255,255},RGB{204,203,201},RGB{200,100,0},RGB{255,1,1},RGB{1,2,3},RGB{0,0,0}}){
  RGB previous{};
  for(unsigned gain=0;gain<=1000;gain++){
   auto v=visibleScale(colour,gain,1000),rot=visibleScale({colour.g,colour.b,colour.r},gain,1000);
   assert(v.r==rot.b&&v.g==rot.r&&v.b==rot.g);
   assert(v.r>=previous.r&&v.g>=previous.g&&v.b>=previous.b);
   assert(v.r<=colour.r&&v.g<=colour.g&&v.b<=colour.b);previous=v;
  }
 }
 RGB f[PHYSICAL_COUNT];
 for(int budget=Config::PANEL_IDLE_MA;budget<=MAX_TOTAL_MA;budget++){
  clear(f);for(int i=0;i<64;i++)f[i]={204,uint8_t(i%205),uint8_t((i*3)%205)};
  unsigned minimumSum=0;for(auto c:f){auto floor=visibleScale(c,1,65535);minimumSum+=floor.r+floor.g+floor.b;}
  const auto minimumBudget=Config::PANEL_IDLE_MA+(minimumSum*20+254)/255;
  capVisibleCurrent(f,budget);assert(estimatedMilliAmps(f)<=budget);
  for(int y=0;y<PHYSICAL_WIDTH;y++)for(int x=0;x<PHYSICAL_WIDTH;x++){
   RGB c=f[y*PHYSICAL_WIDTH+x];
   if(y<8&&x<8&&budget>=minimumBudget)assert(c.r||c.g||c.b);
   if(y>=8||x>=8)assert(!(c.r||c.g||c.b));
   assert(c.r<=204&&c.g<=204&&c.b<=204);
  }
 }
 // All-white floors require three counts per pixel; when a budget cannot
 // fund that, strict current limiting wins over visibility.
 for(unsigned budget=64;budget<=200;budget++){
  for(auto& c:f)c={204,204,204};capVisibleCurrent(f,budget);assert(estimatedMilliAmps(f)<=budget);
  for(auto c:f)assert(c.r==c.g&&c.g==c.b);
 }
 puts("PASS: RGB load limiting across all panel budgets.");
}
