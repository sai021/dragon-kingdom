#include "../DragonPrototype/DragonCore.h"
#include <assert.h>
#include <math.h>
#include <stdio.h>
#include <stdint.h>
using namespace Dragon;
int main() {
 Wiring w;
 assert(w.mirror);
 assert(logicalIndex(0,0,w)==7 && logicalIndex(7,0,w)==0);
 assert(logicalIndex(0,7,w)==56 && logicalIndex(7,7,w)==63);
 w.mirror=false; // Check the underlying serpentine wiring separately.
 assert(logicalIndex(0,0,w)==0);assert(logicalIndex(7,0,w)==7);
 assert(logicalIndex(0,1,w)==15);assert(logicalIndex(7,1,w)==8);
 assert(logicalIndex(0,7,w)==63);assert(logicalIndex(7,7,w)==56);
 assert(logicalIndex(-1,0,w)==-1);assert(logicalIndex(8,0,w)==-1);
 assert(PHYSICAL_WIDTH==8 && PHYSICAL_COUNT==64);
 assert(physicalIndex(8,0,w)==-1 && physicalIndex(0,8,w)==-1);
 w.offsetX=1;assert(logicalIndex(0,0,w)==-1);w.offsetX=0;
 w.offsetY=1;assert(logicalIndex(0,0,w)==-1);w.offsetY=0;
 unsigned configurations=0;
 for(int serp=0;serp<2;serp++)for(int cols=0;cols<2;cols++)for(int mirror=0;mirror<2;mirror++)for(int rot=0;rot<4;rot++) {
  w.serpentine=serp;w.columns=cols;w.mirror=mirror;w.quarterTurns=rot;
  bool seen[PHYSICAL_COUNT]={};for(int y=0;y<PHYSICAL_WIDTH;y++)for(int x=0;x<PHYSICAL_WIDTH;x++){int i=physicalIndex(x,y,w);assert(i>=0&&i<PHYSICAL_COUNT&&!seen[i]);seen[i]=true;}
  for(int oy=0;oy<=PHYSICAL_WIDTH-LOGICAL_WIDTH;oy++)for(int ox=0;ox<=PHYSICAL_WIDTH-LOGICAL_WIDTH;ox++){
   w.offsetX=ox;w.offsetY=oy;RGB f[PHYSICAL_COUNT];clear(f);bool used[PHYSICAL_COUNT]={};
   for(int y=0;y<8;y++)for(int x=0;x<8;x++){int i=logicalIndex(x,y,w);assert(i>=0&&i<PHYSICAL_COUNT&&!used[i]);used[i]=true;f[i]={255,255,255};}
   capCurrent(f,1000);assert(estimatedMilliAmps(f)<=1000);
   int active=0;for(int i=0;i<PHYSICAL_COUNT;i++){if(used[i]){assert(f[i].r>0);active++;}else assert(f[i].r==0&&f[i].g==0&&f[i].b==0);}assert(active==64);configurations++;
  }
 }
 const int expected[ZONE_COUNT]={0,4,4,1,1,10,10,5,13,16};int count[ZONE_COUNT]={};for(auto& row:ZONES)for(Zone z:row){assert(z<ZONE_COUNT);count[z]++;}for(int z=0;z<ZONE_COUNT;z++)assert(count[z]==expected[z]);
 RGB all[PHYSICAL_COUNT];for(auto& c:all)c={255,255,255};capCurrent(all,1000);assert(estimatedMilliAmps(all)<=1000);capCurrent(all,Config::PANEL_IDLE_MA);assert(channelSum(all)==0);
 assert(fabs(sourceVolts(5250.0f*20000.0f/120000.0f)-5.25f*Config::VOLTAGE_CALIBRATION)<.0001f);
 TouchFilter t;uint32_t now=0;for(int i=0;i<64;i++){now+=20;assert(t.update(10000,now)==0);}assert(t.ready&&!t.pressed);
 now+=20;assert(t.update(20000,now)==0);now+=20;assert(t.update(10000,now)==0);assert(!t.pressed); // short spike
 now+=20;assert(t.update(20000,now)==0);now+=60;assert(t.update(20000,now)==1);assert(t.pressed);
 float baseline=t.baseline;for(int i=0;i<100;i++){now+=20;assert(t.update(20000,now)==0);}assert(t.baseline==baseline); // a hold cannot be calibrated away
 now+=20;assert(t.update(10000,now)==0);now+=60;assert(t.update(10000,now)==-1);assert(!t.pressed);
 t.candidateSince=UINT32_MAX-20;t.candidate=true;t.pressed=false;assert(t.update(20000,50)==1); // millis wrap
 assert(t.update(0,70)==0);assert(!t.ready&&!t.pressed); // invalid sample cannot keep dimming
 printf("PASS: %u layout/offset combinations, 64 physical LEDs, zone counts, current estimate, divider, S3 touch debounce/hold/wrap.\n",configurations);
}
