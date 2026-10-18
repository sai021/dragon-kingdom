#pragma once
// Included within DragonWeb, using the existing authenticated request helpers.
bool unsignedArgument(const char* name,uint32_t& result){
 String value=server.arg(name);if(!value.length()||value.length()>10)return false;
 for(size_t i=0;i<value.length();i++)if(value[i]<'0'||value[i]>'9')return false;
 char* end=nullptr;unsigned long number=strtoul(value.c_str(),&end,10);
 if(*end||number>4102444800ul)return false;result=uint32_t(number);return true;
}
bool clockArguments(DragonAlarm::Settings& value,uint32_t& epoch){
 int offset,count;
 if(!unsignedArgument("epoch",epoch)||epoch<1704067200u||
    !unsignedArgument("validFrom",value.validFrom)||!unsignedArgument("validUntil",value.validUntil)||
    !numberArgument("offset",-840,840,offset)||!numberArgument("count",0,DragonAlarm::TRANSITIONS,count))return false;
 value.offset=offset;value.count=count;
 for(uint8_t i=0;i<DragonAlarm::TRANSITIONS;i++)value.changes[i]={};
 for(int i=0;i<count;i++){
  String at="at"+String(i),zone="offset"+String(i);
  if(!unsignedArgument(at.c_str(),value.changes[i].at)||!numberArgument(zone.c_str(),-840,840,offset))return false;
  value.changes[i].offset=offset;
 }
 return DragonAlarm::valid(value)&&DragonAlarm::clockReady(value,epoch);
}
void syncAlarmClock(uint32_t epoch){timeval clock{time_t(epoch),0};settimeofday(&clock,nullptr);}
String alarmJson(){
 const auto& a=sunrise;const auto& s=a.settings;
 return String("{\"enabled\":")+(s.enabled?"true":"false")+",\"minute\":"+String(s.minute)+
  ",\"duration\":"+String(s.duration)+",\"clockReady\":"+(DragonAlarm::clockReady(s,alarmEpoch())?"true":"false")+
  ",\"active\":"+(a.active?"true":"false")+",\"preview\":"+(a.preview?"true":"false")+
  ",\"progress\":"+String(a.level/10)+"}";
}
void registerAlarmRoutes(){
 server.on("/api/alarm",HTTP_GET,[]{if(authorize())reply(200,alarmJson());});
 server.on("/api/alarm/clock",HTTP_POST,[]{
  if(!authorize())return;auto value=sunrise.settings;uint32_t epoch;
  if(!clockArguments(value,epoch)){server.send(400,"text/plain","Check your phone's clock and try again.");return;}
  // Sync in RAM without a flash write on every page open. Saving the alarm persists rules.
  sunrise.settings=value;syncAlarmClock(epoch);reply(200,alarmJson());
 });
 server.on("/api/alarm",HTTP_POST,[]{
  if(!authorize())return;auto value=sunrise.settings;int enabled,minute,duration;uint32_t epoch;
  if(!numberArgument("enabled",0,1,enabled)||!numberArgument("minute",0,1439,minute)||
     !numberArgument("duration",1,120,duration)){server.send(400,"text/plain","Choose a wake-up time and a sunrise lasting 1 to 120 minutes.");return;}
  value.enabled=enabled;value.minute=minute;value.duration=duration;
  if(!clockArguments(value,epoch)){server.send(400,"text/plain","Check your phone's clock and try again.");return;}
  if(!saveAlarmSettings(value)){server.send(500,"text/plain","Alarm could not be saved. Try again.");return;}
  syncAlarmClock(epoch);reply(200,alarmJson());
 });
 server.on("/api/alarm/preview",HTTP_POST,[]{if(!authorize())return;sunrise.startPreview(millis());reply(200,alarmJson());});
 server.on("/api/alarm/stop",HTTP_POST,[]{if(!authorize())return;sunrise.stop();reply(200,alarmJson());});
}
