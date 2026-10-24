#define CONFIG_IDF_TARGET_ESP32S3 1
#include "../DragonPrototype/DragonPrototype.ino"
#include <cassert>
int failLevel=9999;
float voltage(){return (shownTotal>unsigned(failLevel)?4.40f:5.00f)/Config::VOLTAGE_CALIBRATION;}
unsigned transientReads=0;
float transientVoltage(){
 if(shownTotal==800&&transientReads++<150)return 4.40f/Config::VOLTAGE_CALIBRATION;
 return 5.00f/Config::VOLTAGE_CALIBRATION;
}
void reset(){fakeTime=0;voltageReads=0;peakTotal=0;touchGain=100;voltageHook=voltage;failureSavedThisBoot=false;computerUsbMode=false;}
float wrongDividerVoltage(){return 5.0f/1.79f/Config::VOLTAGE_CALIBRATION;}
int main(){
 for(auto& g:zoneGain)g=100;for(auto& g:pixelGain)g=100;
 reset();startupStabilize();assert(fakeTime==2800&&shownTotal==BASE_TOTAL_MA&&peakTotal==BASE_TOTAL_MA+1&&voltageReads==0);
 reset();startupCheck();assert(operatingTotal==2400&&startupPower.tested==6);
 assert(voltageReads==900&&fakeTime==7500&&peakTotal==2400&&storeWrites==0);
 for(auto s:startupPower.stats)assert(s.count==30);
 reset();startupCheck(true);assert(computerUsbMode&&operatingTotal==400&&startupPower.tested==2);
 assert(voltageReads==300&&fakeTime==5700&&peakTotal==400&&storeWrites==0);
 assert(!strcmp(startupResult,"computer USB cap"));
 // A one-window droop is unloaded and retried once instead of reducing the session ceiling.
 reset();transientReads=0;voltageHook=transientVoltage;startupCheck();
 assert(operatingTotal==2400&&startupPower.failure==0&&startupPower.stats[3].count==30);
 assert(voltageReads==1050&&fakeTime==8250&&storeWrites==0);
 unsigned expectedWrites=0;
 for(int ceiling: {0,300,400,500,800,1600}){
  failLevel=ceiling;reset();startupCheck();assert(operatingTotal==ceiling);
  assert(storeWrites==++expectedWrites&&failureSavedThisBoot&&savedFailureValid);
  assert(savedFailure.failure==1&&savedFailure.maximum==ceiling&&validFailureRecord(savedFailure));
  assert(validFailureHistory(failureHistory)&&failureHistory.count==min(expectedWrites,unsigned(SavedFailureHistory::CAPACITY)));
  assert(shownTotal==BASE_TOTAL_MA);
 }
 auto retained=failureHistory;failLevel=9999;reset();startupCheck();auto reads=voltageReads;
 assert(storeWrites==expectedWrites&&!failureSavedThisBoot&&!memcmp(&retained,&failureHistory,sizeof(retained)));
 for(int i=0;i<10000;i++)loop();assert(voltageReads==reads&&operatingTotal==2400);
 // A new session recalibrates from the baseline, without reading a saved ceiling.
 failLevel=800;reset();startupCheck();assert(operatingTotal==800);
 assert(storeWrites==++expectedWrites&&savedFailure.maximum==800);
 // Failure codes remain visible even when ambient light would disable normal output.
 operatingTotal=0;ambientGain=touchGain=0;
 for(int code=1;code<=5;code++){
  startupPower.failure=code;
  for(int pulse=0;pulse<code;pulse++){
   composeFrame(pulse*1000+100);assert(channelSum(frame)==128);
   assert(estimatedMa+Config::ESP_RESERVE_MA<300);
   composeFrame(pulse*1000+700);assert(channelSum(frame)==0);
  }
  composeFrame(code*1000+100);assert(channelSum(frame)==0);
 }
 // Corruption and incomplete records are rejected; valid records round-trip.
 auto record=makeFailureRecord(startupPower);assert(validFailureRecord(record));
 record.checksum^=1;assert(!validFailureRecord(record));
 auto history=failureHistory;assert(validFailureHistory(history));history.checksum^=1;assert(!validFailureHistory(history));
 // A chip-bound correction repairs divider sensing without lifting the USB cap.
 failLevel=9999;reset();voltageHook=wrongDividerVoltage;voltageCorrection=1790;startupCheck(true);
 assert(operatingTotal==400&&peakTotal<=400&&fabs(startupPower.lastVolts-5.0f)<.03f);
 auto unit=DragonVoltage::make(123,1790);voltageCorrection=DragonVoltage::correction(unit,456);
 reset();voltageHook=wrongDividerVoltage;startupCheck(true);assert(operatingTotal==0&&startupPower.failure==2);
 puts("PASS: six levels, fallback, two-second indicator, persistent failure record, no runtime voltage reads.");
}
