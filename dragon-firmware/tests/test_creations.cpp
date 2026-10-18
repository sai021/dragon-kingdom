#define CONFIG_IDF_TARGET_ESP32S3 1
#include "../DragonPrototype/DragonPrototype.ino"
#include <cassert>
#include <cstdio>
int main(){
 assert(library.begin());auto data=library.data;data.profiles[1].used=1;strcpy(data.profiles[1].name,"Test");data.active=1;auto& c=data.customs[0];c.used=1;c.owner=1;c.base=0;strcpy(c.name,"Bright test");c.colorMask=(1u<<ZONE_COUNT)-1;
 for(auto& color:c.colors)color={255,255,255};for(auto& mask:c.effectZones)mask=c.colorMask;
 data.profiles[1].count=2;data.profiles[1].favorites[0]=PRESET_COUNT;data.profiles[1].favorites[1]=0;assert(library.save(data));
 for(auto& gain:zoneGain)gain=100;for(auto& gain:pixelGain)gain=100;
 setPalette(PRESET_COUNT);setBrightness(100);touchGain=ambientGain=100;
 for(uint16_t limit:{300,400,500,800,1600,2400}){
  operatingTotal=limit;
  for(int effect=0;effect<6;effect++)for(uint32_t now=0;now<6000;now+=137){mode=Mode(effect);composeFrame(now);assert(estimatedMa+runtimeReserve(limit)<=limit);for(auto pixel:frame)assert(pixel.r<=204&&pixel.g<=204&&pixel.b<=204);}
 }
 mode=ZONE_VIEW;setPalette(library.next(PRESET_COUNT));assert(palette==0);setPalette(library.next(palette));assert(palette==PRESET_COUNT);
 rememberLighting();toggleLighting();assert(mode==OFF);toggleLighting();assert(palette==PRESET_COUNT&&mode==ZONE_VIEW);
 auto empty=library.data;empty.profiles[2].used=1;strcpy(empty.profiles[2].name,"Empty");empty.active=2;assert(library.save(empty));assert(!DragonLibrary::contains(library.data,0,2));mode=OFF;fakeDigital=1;updateTouch(fakeTime+2000);assert(mode==OFF);
 auto filled=library.data;filled.profiles[2].count=1;filled.profiles[2].favorites[0]=2;filled.customs[1].used=1;filled.customs[1].owner=2;filled.customs[1].base=0;strcpy(filled.customs[1].name,"Extra");assert(library.save(filled));assert(library.next(255)==2);assert(library.next(2)==PRESET_COUNT+1);assert(library.next(PRESET_COUNT+1)==2);
 puts("PASS: custom power caps, profile collection cycling, sleep/wake and empty-profile touch isolation.");
}
