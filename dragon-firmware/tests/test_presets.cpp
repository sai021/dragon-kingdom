#define CONFIG_IDF_TARGET_ESP32S3 1
#include "../DragonPrototype/DragonPrototype.ino"
#include <cassert>
int main(){
 assert(ACTIVE_PRESET_COUNT==79);
 assert(PRESET_COUNT==81&&!strcmp(DRAGON_PRESETS[0].id,"blue"));
 for(auto& g:zoneGain)g=100;for(auto& g:pixelGain)g=100;
 touchGain=ambientGain=100;setBrightness(100);
 for(int p=0;p<PRESET_COUNT;p++){
  if(PRESET_RETIRED[p])continue;
  for(auto c:DRAGON_PRESETS[p].pixels)assert(c.r || c.g || c.b);
  char command[80];snprintf(command,sizeof(command),"dragon %s",DRAGON_PRESETS[p].id);handleCommand(command);assert(palette==p);
  for(auto budget:StartupPower::levels)for(int t=1;t<12;t++){
   operatingTotal=budget;composeFrame(t*371);assert(estimatedMa+Config::ESP_RESERVE_MA<=budget);
   for(auto c:frame)assert(c.r<=204&&c.g<=204&&c.b<=204);
  }
 }
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
