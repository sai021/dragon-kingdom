#define CONFIG_IDF_TARGET_ESP32S3 1
#include "../DragonPrototype/DragonPrototype.ino"
#include <cassert>
void cmd(const char* s){char line[80];strcpy(line,s);handleCommand(line);}
void advance(uint32_t ms){for(uint32_t t=0;t<ms;t+=10){fakeTime+=10;updateLight(fakeTime);}}
void touch(bool value,uint32_t dt){fakeDigital=value;fakeTime+=dt;updateTouch(fakeTime);}
void tap(){touch(true,20);touch(true,60);touch(false,80);touch(false,60);}
int main(){
 operatingTotal=1600;setBrightness(100);touchGain=100;ambientGain=100;
 for(auto& g:zoneGain)g=100;for(auto& g:pixelGain)g=100;
 mode=SOLID;solidColor={255,255,255};composeFrame(100);RGB base[64];memcpy(base,frame,sizeof(frame));
 ambientGain=60;touchGain=50;composeFrame(100);
 for(int i=0;i<64;i++){auto expected=scaled(scaled(base[i],60,100),50,100);assert(!memcmp(&frame[i],&expected,sizeof(RGB)));}
 // Dark-room gain and minimum manual glow must not round an awake pixel to
 // black. Retain only pixels the session power budget can already illuminate.
 for(uint16_t limit:{300,400,500,800,1600,2400}){
  operatingTotal=limit;mode=ZONE_VIEW;
  for(uint8_t p=0;p<PRESET_COUNT;p++){
   if(PRESET_RETIRED[p])continue;setPalette(p);
   ambientGain=touchGain=100;composeFrame(100);memcpy(base,frame,sizeof(frame));
   ambientGain=touchGain=10;composeFrame(100);
   for(int i=0;i<64;i++){
    bool lit=base[i].r||base[i].g||base[i].b;
    assert(bool(frame[i].r||frame[i].g||frame[i].b)==lit);
   }
   assert(estimatedMa+runtimeReserve(limit)<=limit);
  }
 }
 operatingTotal=400;mode=SOLID;solidColor={0,0,0};composeFrame(100);assert(channelSum(frame)==0);
 // Fine USB measurement uses raw scaling, bypassing the visibility floor and
 // both user/ambient gains, without modifying profiles or raising power limits.
 auto diagnosticWrites=storeWrites;solidColor={255,255,255};cmd("testglow 5");assert(rawGlowTest==5);
 ambientGain=touchGain=10;
 for(uint16_t limit:{300,400,500,800,1600,2400}){
  operatingTotal=limit;rawGlowTest=0;ambientGain=touchGain=100;composeFrame(100);memcpy(base,frame,sizeof(frame));
  ambientGain=touchGain=10;
  for(uint8_t percent=1;percent<=10;percent++){
   rawGlowTest=percent;composeFrame(100);
   for(int i=0;i<64;i++){auto expected=scaled(base[i],percent,100);assert(!memcmp(&frame[i],&expected,sizeof(RGB)));}
   assert(estimatedMa+runtimeReserve(limit)<=limit);
  }
 }
 cmd("testglow 0");assert(rawGlowTest==0);cmd("testglow 4");cmd("brightness 10");assert(rawGlowTest==0);
 assert(storeWrites==diagnosticWrites);
 operatingTotal=1600;
 for(int b=1;b<=100;b++){setBrightness(b);assert(brightness>=10&&brightness<=100&&brightness%10==0);}
 autoLight=false;setBrightness(50);touchGain=100;lastFade=lastLight=fakeTime=0;lightReads=0;
 advance(1500);assert(touchGain==50&&lightReads==0); // fading, without extra ADC load
 autoLight=true;fakeLight=0;advance(1000);assert(lightReads==4);
 advance(5000);assert(ambient.targetGain()==10&&ambientGain==10);
 // Every ambient bin has a stable target, and small boundary noise cannot chatter.
 for(int step=1;step<=10;step++){
  AmbientLight a;
  uint16_t input=step==1?a.dark:(step==10?a.bright:uint32_t(a.dark)+uint32_t(a.bright-a.dark)*(2*step-1)/18);
  for(uint32_t t=0;t<=10000;t+=250)a.update(input,t);
  assert(a.targetGain()==step*10);
 }
 AmbientLight a;for(uint32_t t=0;t<6000;t+=250)a.update(2000,t);auto before=a.step;
 for(uint32_t t=6000;t<12000;t+=250)a.update(t%500?1990:2010,t);assert(a.step==before);
 for(uint32_t t=12000;t<20000;t+=250)a.update(4095,t);assert(!a.night&&a.targetGain()==100);
 for(uint32_t t=20000;t<30000;t+=250)a.update(0,t);assert(a.night&&a.targetGain()==10);
 setBrightness(100);touchGain=100;mode=ZONE_VIEW;gestures=TouchGestures{};lastTouch=0;fakeTime=10000;
 touch(true,20);touch(true,60);touch(true,720);assert(brightness==90);
 touch(true,400);assert(brightness==80);touch(false,20);touch(false,60);assert(dimUp);
 tap();tap();assert(mode==OFF);advance(3000);composeFrame(fakeTime);assert(channelSum(frame)==0);
 // Daylight stays visible, but explicit sleep still works.
 ambient.night=false;ambientGain=100;tap();touch(false,450);advance(3000);assert(autoLight&&mode!=OFF);composeFrame(fakeTime);assert(channelSum(frame)>0);
 auto writes=storeWrites;cmd("brightness 70");cmd("auto off");assert(storeWrites==writes);
 cmd("light calibrate 0 2515");assert(ambient.dark==377&&ambient.bright==3305);
 puts("PASS: multiplicative hierarchy, ten touch/light steps, smooth fades, threshold dwell, 4Hz ADC, gestures and calibration.");
}
