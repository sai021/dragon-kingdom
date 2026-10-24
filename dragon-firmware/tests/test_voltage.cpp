#include "../DragonPrototype/StartupPower.h"
#include "../DragonPrototype/SensorControl.h"
#include <cassert>
#include "../DragonPrototype/VoltageCalibration.h"
#include <cstdio>
using namespace Dragon;
void fill(VoltageStats& s,float a,float b){for(int i=0;i<30;i++)s.add(i%2?a:b);}
int main(){
 auto calibration=DragonVoltage::make(0x123456789abcULL,1790);
 assert(DragonVoltage::correction(calibration,0x123456789abcULL)==1790);
 assert(DragonVoltage::correction(calibration,0x123456789abdULL)==1000);
 auto damaged=calibration;damaged.permille=1700;assert(!DragonVoltage::valid(damaged,calibration.identity));
 assert(!DragonVoltage::valid(DragonVoltage::make(calibration.identity,499),calibration.identity));
 assert(!DragonVoltage::valid(DragonVoltage::make(calibration.identity,3001),calibration.identity));
 assert(fabs(2.8f*DragonVoltage::correction(calibration,calibration.identity)/1000.0f-5.012f)<.0001f);
 uint32_t noisy[]={0,902,899,900,1200};assert(medianFive(noisy)==900);
 VoltageStats s;fill(s,4.9,5.1);assert(fabs(s.mean-5)<.001&&fabs(s.range()-.2)<.001&&fabs(s.deviation()-.1)<.001);
 StartupPower p;fill(p.stats[2],4.99,5.01);assert(p.accept(2));
 fill(p.stats[3],4.91,4.93);assert(p.accept(3)&&p.maximum==800);
 fill(p.stats[4],4.54,4.86);assert(!p.accept(4)&&p.maximum==800);
 StartupPower relative;fill(relative.stats[2],5.39,5.41);assert(relative.accept(2));
 fill(relative.stats[3],4.8,4.82);assert(!relative.accept(3)&&relative.maximum==500);
 StartupPower low;fill(low.stats[2],4.48,4.51);assert(!low.accept(2)&&low.maximum==0);
 StartupPower noise;fill(noise.stats[2],4.97,5.03);assert(noise.accept(2));
 fill(noise.stats[3],4.92,5.08);assert(noise.accept(3)); // within 3x baseline, above absolute floor
 StartupPower rising;fill(rising.stats[2],4.99,5.01);assert(rising.accept(2));
 for(int i=0;i<29;i++)rising.stats[3].add(5.02f);rising.stats[3].add(5.45f);
 assert(rising.accept(3)&&rising.maximum==800); // upward spike is diagnostic only
 StartupPower over;fill(over.stats[2],5.0,5.02);assert(over.accept(2));
 fill(over.stats[3],5.51,5.52);assert(!over.accept(3)&&over.failure==5);
 StartupPower few;few.stats[2].add(5);assert(!few.accept(2));
 puts("PASS: asymmetric droop, upward spikes, overvoltage, relative floor, and sample completeness.");
}
