#define CONFIG_IDF_TARGET_ESP32S3 1
#include "../DragonPrototype/DragonPrototype.ino"
#include <cassert>
int main(){
 assert(ACTIVE_PRESET_COUNT==79);
 assert(PRESET_COUNT==81&&!strcmp(DRAGON_PRESETS[0].id,"blue"));
 for(auto& g:zoneGain)g=100;for(auto& g:pixelGain)g=100;
 touchGain=100;ambientGainPermille=1000;setBrightness(100);
 for(int p=0;p<PRESET_COUNT;p++){
  if(PRESET_RETIRED[p])continue;
  for(auto c:DRAGON_PRESETS[p].pixels)assert(c.r || c.g || c.b);
  char command[80];snprintf(command,sizeof(command),"dragon %s",DRAGON_PRESETS[p].id);handleCommand(command);assert(palette==p);
  for(auto budget:StartupPower::levels)for(int t=1;t<12;t++){
   operatingTotal=budget;composeFrame(t*371);assert(estimatedMa+Config::ESP_RESERVE_MA<=budget);
   for(auto c:frame)assert(c.r<=204&&c.g<=204&&c.b<=204);
  }
 }
 // Glitter dims the entire silhouette, retains bright wing sparkles and obeys power caps.
 setPalette(0);mode=PATRONUS_GLITTER;operatingTotal=StartupPower::levels[0];
 // Inspect uncapped background via a non-wing pixel in a full frame at the largest budget.
 operatingTotal=StartupPower::levels[sizeof(StartupPower::levels)/sizeof(StartupPower::levels[0])-1];
 bool sawSparkle=false;
 for(uint32_t t=0;t<420;t+=35){composeFrame(t);for(int y=0;y<8;y++)for(int x=0;x<8;x++){
  RGB c=frame[logicalIndex(x,y,wiring)];
  if(!fullWingZone(ZONES[y][x]))assert(c.r<=20&&c.g<=20&&c.b<=20);
  else if(c.r>100&&c.g>100&&c.b>100)sawSparkle=true;
 }}assert(sawSparkle);
 // Sparkles add light without darkening saturated base colours.
 auto sparkle=sparkleRgb({255,30,0},{255,255,255},255);
 assert(sparkle.r==255&&sparkle.g==255&&sparkle.b==255);
 for(uint16_t budget:StartupPower::levels){
  operatingTotal=budget;mode=PATRONUS_GLITTER;
  for(uint32_t t=0;t<4200;t+=35){composeFrame(t);assert(estimatedMa+Config::ESP_RESERVE_MA<=budget);}
 }
 setPalette(PRESET_COUNT);assert(palette==0);
 auto old=palette;char invalid[]="dragon missing";handleCommand(invalid);assert(palette==old);
 mode=OFF;composeFrame(9999);assert(channelSum(frame)==0);
 puts("PASS: 81 dragons, command selection, wrap and 3564 current-limited animation frames.");
}
