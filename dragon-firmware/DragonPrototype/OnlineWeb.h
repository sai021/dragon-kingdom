#pragma once
DragonOnline::Transport onlineTransport;
DragonOnline::Manifest onlineManifest;
String onlineText,onlineMessage="Connect home Wi-Fi to check for signed releases.";
char onlineOwner[65]{};
String onlineChannel="release";
bool onlineReturnRelease=false;
enum OnlinePhase:uint8_t {ONLINE_IDLE,ONLINE_CHECKING,ONLINE_READY,ONLINE_CURRENT,ONLINE_INSTALLING,ONLINE_FAILED,ONLINE_RESTARTING};
OnlinePhase onlinePhase=ONLINE_IDLE;
String onlineCanonical(const DragonOnline::Manifest& value){return String("dragon-update-v2\n")+value.board+"\n"+value.tag+"\n"+String(value.size)+"\n"+value.hash+"\n"+String(value.capabilities)+"\n"+String(value.schema)+"\n";}
void failOnline(const String& text){onlineTransport.cancel();if(onlinePhase==ONLINE_INSTALLING&&transfer.active)abortUpdate();onlineBusy=false;onlinePhase=ONLINE_FAILED;onlineMessage=text;onlineText="";}
String onlineJson(){return String("{\"phase\":")+String(unsigned(onlinePhase))+",\"busy\":"+(onlineBusy?"true":"false")+",\"current\":"+quote(DragonOnline::CURRENT_TAG)+",\"channel\":"+quote(onlineChannel)+",\"release\":"+quote(onlineManifest.tag)+",\"message\":"+quote(onlineMessage)+",\"progress\":"+String(onlinePhase==ONLINE_INSTALLING&&transfer.size?transfer.offset*100/transfer.size:0)+"}";}
bool onlineOwnerValid(){return parentSession.accepts(onlineOwner,millis());}
void registerOnlineRoutes(){
 server.on("/api/update/online",HTTP_GET,[]{if(!authorizeParent())return;reply(200,onlineJson());});
 server.on("/api/update/online/check",HTTP_POST,[]{
  if(!authorizeParent())return;
  if(onlineBusy||onlineTransport.running()||transfer.active||connecting||joinAfterReply||rebootPending){server.send(409,"text/plain","Wait for the current operation to finish.");return;}
  if(ap||WiFi.status()!=WL_CONNECTED||alarmEpoch()<1704067200){server.send(409,"text/plain","Join home Wi-Fi with internet after setup Wi-Fi closes, and sync the clock first.");return;}
  String channel=server.arg("channel");if(!channel.length())channel="release";
  if(channel!="release"&&channel!="beta"){server.send(400,"text/plain","Choose release or beta updates.");return;}
  onlineReturnRelease=server.arg("intent")=="return-release";onlineChannel=channel;onlineManifest={};onlineText="";strcpy(onlineOwner,parentSession.token);
  String url=String("https://github.com/sai021/dragon-kingdom/releases/")+(onlineChannel=="beta"?"download/firmware-beta/":"latest/download/")+"dragon-"+boardName()+".manifest";
  if(!onlineTransport.start(url.c_str(),DragonOnline::MANIFEST_MAX)){server.send(503,"text/plain","Could not start HTTPS. Try again or upload a file.");return;}
  onlineBusy=true;onlinePhase=ONLINE_CHECKING;onlineMessage="Checking the latest signed release on GitHub...";reply(202,onlineJson());
 });
 server.on("/api/update/online/install",HTTP_POST,[]{
  if(!authorizeParent())return;
  if(onlinePhase!=ONLINE_READY||onlineBusy||onlineTransport.running()||transfer.active||!firmwareValidated||connecting||joinAfterReply||rebootPending){server.send(409,"text/plain","Check for a signed release first, and wait for startup validation.");return;}
  if(!onlineOwnerValid()||strcmp(onlineOwner,parentSession.token)||server.arg("release")!=onlineManifest.tag){server.send(409,"text/plain","Parent session or release changed. Check for updates again.");return;}
  if(WiFi.status()!=WL_CONNECTED){server.send(409,"text/plain","Home Wi-Fi is unavailable. Existing firmware was kept.");return;}
  // Recheck the signed metadata immediately before touching flash.
  if(!DragonCompatibility::compatible(onlineManifest.capabilities,onlineManifest.schema,voltageCalibrationPresent)||!DragonCompatibility::allowed(onlineManifest.tag,DragonOnline::CURRENT_TAG,onlineReturnRelease)||strcmp(onlineManifest.board,boardName())||!verifyUpdateSignature(onlineCanonical(onlineManifest),onlineManifest.signature)){failOnline("Signed release verification failed.");server.send(403,"text/plain",onlineMessage);return;}
  uint8_t digest[32];DragonUpdate::decode(onlineManifest.hash,64,digest,32);
  if(!beginTransfer(onlineManifest.size,digest)){server.send(503,"text/plain","Could not prepare the inactive update slot.");return;}
  String url=String("https://github.com/sai021/dragon-kingdom/releases/download/")+onlineManifest.tag+"/dragon-"+boardName()+".bin";
  if(!onlineTransport.start(url.c_str(),onlineManifest.size)){abortUpdate();server.send(503,"text/plain","Could not start the download. Existing firmware was kept.");return;}
  onlineBusy=true;onlinePhase=ONLINE_INSTALLING;onlineMessage="Downloading verified firmware. Keep power connected.";reply(202,onlineJson());
 });
 server.on("/api/update/online/cancel",HTTP_POST,[]{if(!authorizeParent())return;failOnline("Online update cancelled. Existing firmware was kept.");reply(200,onlineJson());});
}
void serviceOnline(){
 if(!onlineBusy)return;
 if(!onlineOwnerValid()||strcmp(onlineOwner,parentSession.token)){failOnline("Parent session expired or changed. Unlock and check again.");return;}
 DragonOnline::Message message;if(!onlineTransport.read(message))return;
 if(message.kind==DragonOnline::FAILED){char error[513];memcpy(error,message.bytes,message.size);error[message.size]=0;failOnline(error);return;}
 if(onlinePhase==ONLINE_CHECKING){
  if(message.kind==DragonOnline::DATA){if(onlineText.length()+message.size>DragonOnline::MANIFEST_MAX){failOnline("Release metadata is too large.");return;}onlineText.concat((const char*)message.bytes,message.size);return;}
  // Legacy feeds cannot express calibration/schema guarantees. Explain the
  // publication transition; never offer their application for installation.
  if(!strncmp(onlineText.c_str(),"dragon-online-v1",16)||!strncmp(onlineText.c_str(),"dragon-update-v1",16)){onlineManifest={};failOnline("No compatible online release has been published for this firmware yet. Use a matching signed firmware file.");return;}
  if(!DragonOnline::parse(onlineText.c_str(),onlineText.length(),onlineManifest)||strcmp(onlineManifest.board,boardName())||!DragonOnline::channelTag(onlineChannel.c_str(),onlineManifest.tag)||!verifyUpdateSignature(onlineCanonical(onlineManifest),onlineManifest.signature)){onlineManifest={};failOnline("Invalid signature, board or release metadata. Existing firmware was kept.");return;}
  onlineText="";onlineBusy=false;
  if(!DragonCompatibility::compatible(onlineManifest.capabilities,onlineManifest.schema,voltageCalibrationPresent)){failOnline("This release cannot preserve this unit's calibration or saved data. Existing firmware was kept.");return;}
  if(!DragonCompatibility::allowed(onlineManifest.tag,DragonOnline::CURRENT_TAG,onlineReturnRelease)){onlinePhase=ONLINE_CURRENT;onlineMessage="No newer compatible version. Return to Release is a separate deliberate action.";}
  else {onlinePhase=ONLINE_READY;onlineMessage=String("Signed release ")+onlineManifest.tag+" is available. A parent must choose Install.";}
 }else if(onlinePhase==ONLINE_INSTALLING){
  if(message.kind==DragonOnline::DATA){
   if(!transfer.accepts(transfer.offset,message.size)||esp_ota_write(otaHandle,message.bytes,message.size)!=ESP_OK){failOnline("Firmware download or write failed. Existing firmware was kept.");return;}
   mbedtls_sha256_update(&otaHash,message.bytes,message.size);transfer.offset+=message.size;transfer.last=millis();return;
  }
  if(finalizeTransfer()!=200){failOnline("Downloaded firmware failed verification. Existing firmware was kept.");return;}
  onlineBusy=false;onlinePhase=ONLINE_RESTARTING;onlineMessage="Firmware verified. Restarting and validating startup; reconnect in one minute.";
 }
}
