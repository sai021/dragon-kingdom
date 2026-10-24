#pragma once
Preferences restoreStore;
bool restoreStoreReady=false;
bool restoreBlocked=false;
String hexBytes(const void* data,size_t size){const uint8_t* p=(const uint8_t*)data;String out;out.reserve(size*2);for(size_t i=0;i<size;i++){char pair[3];snprintf(pair,3,"%02x",p[i]);out+=pair;}return out;}
DragonBackup::Snapshot makeBackup(){
 DragonBackup::Snapshot value{};value.library=library.data;value.library.checksum=DragonLibrary::checksum(value.library);value.alarm=sunrise.settings;value.rotation=rotation.settings;value.dark=ambient.dark;value.bright=ambient.bright;value.calibrated=lightCalibrated;value.check=DragonBackup::checksum(value);return value;
}
bool queueRestore(const DragonBackup::Snapshot& value){
 DragonBackup::Snapshot check{};
 if(!restoreStoreReady)restoreStoreReady=restoreStore.begin("dragon-restore",false);
 return DragonBackup::valid(value)&&restoreStoreReady&&restoreStore.putBytes("pending",&value,sizeof(value))==sizeof(value)&&restoreStore.getBytes("pending",&check,sizeof(check))==sizeof(check)&&!memcmp(&value,&check,sizeof(value));
}
// Durable redo journal: interrupted multi-namespace restore retries before networking.
// The journal is removed only after every saved record verifies successfully.
bool recoverRestore(){
 restoreStoreReady=restoreStore.begin("dragon-restore",false);if(!restoreStoreReady)return false;
 if(!restoreStore.isKey("pending")){restoreBlocked=false;return true;}
 restoreBlocked=true;
 DragonBackup::Snapshot value{};if(restoreStore.getBytes("pending",&value,sizeof(value))!=sizeof(value)||!DragonBackup::valid(value))return false;
 if(!library.save(value.library)||!saveRotation(value.rotation))return false;
 auto alarm=value.alarm;alarm.check=DragonAlarm::checksum(alarm);DragonAlarm::Settings verify{};
 if(alarmStore.putBytes("settings",&alarm,sizeof(alarm))!=sizeof(alarm)||alarmStore.getBytes("settings",&verify,sizeof(verify))!=sizeof(verify)||memcmp(&alarm,&verify,sizeof(alarm)))return false;
 sunrise.apply(alarm);
 if(value.calibrated){if(!saveLightSettings(value.dark,value.bright))return false;}
 else {if(lightStore.isKey("settings")&&!lightStore.remove("settings"))return false;ambient=AmbientLight{};lightCalibrated=false;}
 if(value.reset){Preferences wifi,parent;if(!wifi.begin("dragon-wifi",false)||!parent.begin("dragon-parent",false))return false;if(wifi.isKey("home")&&!wifi.remove("home"))return false;if(parent.isKey("credential")&&!parent.remove("credential"))return false;}
 bool removed=restoreStore.remove("pending");restoreBlocked=!removed;return removed;
}
// Service keeps the raw journal until an operator has saved a private NVS dump.
// A valid transaction can only be retried, never abandoned by this command.
bool serviceRestoreCommand(const char* line){
 if(strncmp(line,"restore ",8))return false;
 if(!strcmp(line,"restore retry")){bool ok=recoverRestore();Serial.println(ok?"restore_retry=complete restart_required=1":"restore_retry=blocked journal_retained=1");return true;}
 if(!strcmp(line,"restore abandon-invalid EVIDENCE-SAVED")){
  if(!computerUsbMode){Serial.println("restore_recovery=requires_computer_usb");return true;}
  if(!restoreStoreReady||!restoreStore.isKey("pending")){Serial.println("restore_recovery=no_journal");return true;}
  DragonBackup::Snapshot value{};size_t length=restoreStore.getBytesLength("pending");
  if(!length||(length==sizeof(value)&&restoreStore.getBytes("pending",&value,sizeof(value))!=sizeof(value))){Serial.println("restore_recovery=read_failed journal_retained=1");return true;}
  if(length==sizeof(value)&&DragonBackup::valid(value)){Serial.println("restore_recovery=valid_journal_retained retry_required=1");return true;}
  Serial.println(restoreStore.remove("pending")?"restore_recovery=invalid_journal_removed restart_required=1 inspect_all_saved_settings=1":"restore_recovery=remove_failed journal_retained=1");return true;
 }
 Serial.println("restore retry | restore abandon-invalid EVIDENCE-SAVED (USB service only, save raw NVS first)");return true;
}
void registerBackupRoutes(){
 server.on("/api/backup",HTTP_GET,[]{if(!authorizeParent())return;auto value=makeBackup();reply(200,String("{\"format\":\"dragon-backup-v1\",\"data\":")+quote(hexBytes(&value,sizeof(value)))+"}");});
 server.on("/api/restore",HTTP_POST,[]{
  if(!authorizeParent())return;if(onlineBusy||transfer.active||connecting||rebootPending){server.send(409,"text/plain","Wait for the current operation to finish.");return;}
  DragonBackup::Snapshot value{};String text=server.arg("data");
  if(!DragonUpdate::decode(text.c_str(),text.length(),(uint8_t*)&value,sizeof(value))||value.reset||!DragonBackup::valid(value)){server.send(400,"text/plain","Invalid or incompatible backup. Your saved dragons were kept.");return;}
  if(!queueRestore(value)){server.send(500,"text/plain","Could not stage the restore. Your saved dragons were kept.");return;}
  reply(200,"{\"restarting\":true}");rebootPending=true;rebootAt=millis();
 });
 server.on("/api/reset",HTTP_POST,[]{
  if(!authorizeParent())return;if(onlineBusy||transfer.active||connecting||rebootPending||server.arg("confirm")!="RESET"){server.send(409,"text/plain","Finish other operations and type RESET to confirm.");return;}
  DragonBackup::Snapshot value{};DragonLibrary::Library defaults;value.library=defaults.data;value.library.checksum=DragonLibrary::checksum(value.library);value.reset=1;value.check=DragonBackup::checksum(value);
  if(!queueRestore(value)){server.send(500,"text/plain","Could not stage reset.");return;}
  reply(200,"{\"restarting\":true}");rebootPending=true;rebootAt=millis();
 });
 server.on("/api/rotation",HTTP_GET,[]{if(!authorize())return;reply(200,String("{\"enabled\":")+String(rotation.settings.enabled)+",\"shuffle\":"+String(rotation.settings.shuffle)+",\"seconds\":"+String(rotation.settings.seconds)+"}");});
 server.on("/api/rotation",HTTP_POST,[]{
  if(!authorize())return;int enabled,shuffle,seconds;
  if(!numberArgument("enabled",0,1,enabled)||!numberArgument("shuffle",0,1,shuffle)||!numberArgument("seconds",10,86400,seconds)){server.send(400,"text/plain","Choose a rotation interval from 10 to 86400 seconds.");return;}
  DragonRotation::Settings value{};value.enabled=enabled;value.shuffle=shuffle;value.seconds=seconds;
  if(!saveRotation(value)){server.send(500,"text/plain","Rotation could not be saved.");return;}reply(200,"{}");
 });
}
