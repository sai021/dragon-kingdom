#pragma once
// Included inside DragonWeb. Signed manifest is verified BEFORE erasing the inactive slot.
DragonUpdate::Transfer transfer;
esp_ota_handle_t otaHandle=0;
const esp_partition_t* otaTarget=nullptr;
mbedtls_sha256_context otaHash;
uint8_t expectedHash[32]{};
char updateOwner[65]{};
uint32_t rebootAt=0;
void abortUpdate(){if(transfer.active)esp_ota_abort(otaHandle);transfer.active=false;mbedtls_sha256_free(&otaHash);memset(updateOwner,0,sizeof(updateOwner));}
bool updateOwnerAuthorized(){
 if(!authorizeParent())return false;
 if(!transfer.active||strcmp(updateOwner,parentSession.token)){server.send(409,"text/plain","No update belongs to this session. Start again.");return false;}return true;
}
const char* boardName(){
#if CONFIG_IDF_TARGET_ESP32C3
 return "c3";
#else
 return "s3";
#endif
}
bool verifyUpdateSignature(const String& manifest,const String& signature){
 uint8_t sig[256],hash[32];if(!DragonUpdate::decode(signature.c_str(),signature.length(),sig,sizeof(sig)))return false;
 mbedtls_sha256((const uint8_t*)manifest.c_str(),manifest.length(),hash,0);mbedtls_pk_context key;mbedtls_pk_init(&key);
 int rc=mbedtls_pk_parse_public_key(&key,(const uint8_t*)DRAGON_UPDATE_PUBLIC_KEY,sizeof(DRAGON_UPDATE_PUBLIC_KEY));
 if(!rc)rc=mbedtls_pk_verify(&key,MBEDTLS_MD_SHA256,hash,32,sig,sizeof(sig));mbedtls_pk_free(&key);return rc==0;
}
bool beginTransfer(uint32_t size,const uint8_t* digest){
 otaTarget=esp_ota_get_next_update_partition(nullptr);
 if(!otaTarget||size>otaTarget->size||esp_ota_begin(otaTarget,OTA_WITH_SEQUENTIAL_WRITES,&otaHandle)!=ESP_OK)return false;
 transfer.start(size,millis());memcpy(expectedHash,digest,32);strcpy(updateOwner,parentSession.token);mbedtls_sha256_starts(&otaHash,0);return true;
}
int finalizeTransfer(){
 if(!transfer.complete())return 409;uint8_t hash[32];mbedtls_sha256_finish(&otaHash,hash);
 if(!DragonParent::equal(hash,expectedHash,32)){abortUpdate();return 403;}
 esp_err_t rc=esp_ota_end(otaHandle);transfer.active=false;mbedtls_sha256_free(&otaHash);
 if(rc!=ESP_OK||esp_ota_set_boot_partition(otaTarget)!=ESP_OK)return 400;
 rebootPending=true;rebootAt=millis();return 200;
}
void registerUpdateRoutes(){
 mbedtls_sha256_init(&otaHash);
 server.on("/api/update",HTTP_GET,[]{if(!authorizeParent())return;reply(200,String("{\"board\":")+quote(boardName())+",\"active\":"+(transfer.active?"true":"false")+",\"offset\":"+String(transfer.offset)+"}");});
 server.on("/api/update/start",HTTP_POST,[]{
  if(!authorizeParent())return;uint32_t size=0;uint8_t digest[32],signature[256];
  String sha=server.arg("sha256"),sig=server.arg("signature");
  if(server.arg("board")!=boardName()||!unsignedArgument("size",size)||!size||size>DragonUpdate::MAX_IMAGE||!DragonUpdate::decode(sha.c_str(),sha.length(),digest,sizeof(digest))||!DragonUpdate::decode(sig.c_str(),sig.length(),signature,sizeof(signature))){server.send(400,"text/plain","Wrong board or invalid signed package.");return;}
  if(onlineBusy||!firmwareValidated||transfer.active||connecting||joinAfterReply||rebootPending){server.send(409,"text/plain","Wait for the current operation to finish.");return;}
  String manifest=String("dragon-update-v1\n")+boardName()+"\n"+String(size)+"\n"+sha+"\n";
  if(!verifyUpdateSignature(manifest,sig)){server.send(403,"text/plain","Firmware signature did not match. Download the official package.");return;}
  if(!beginTransfer(size,digest)){server.send(503,"text/plain","Update unavailable. Initial USB migration or startup validation may be required.");return;}
  reply(200,"{\"offset\":0}");
 });
 server.on("/api/update/chunk",HTTP_POST,[]{
  if(!updateOwnerAuthorized())return;if(onlineBusy){server.send(409,"text/plain","An online firmware operation is in progress.");return;}uint32_t at;String text=server.arg("data");uint8_t bytes[512];size_t count=text.length()/2;
  if(!unsignedArgument("offset",at)||!transfer.accepts(at,count)||!DragonUpdate::decode(text.c_str(),text.length(),bytes,count)){server.send(409,"text/plain","Unexpected update chunk. Start the update again.");return;}
  if(esp_ota_write(otaHandle,bytes,count)!=ESP_OK){abortUpdate();server.send(500,"text/plain","Firmware write failed. Existing firmware kept.");return;}
  mbedtls_sha256_update(&otaHash,bytes,count);transfer.offset+=count;transfer.last=millis();reply(200,String("{\"offset\":")+String(transfer.offset)+"}");
 });
 server.on("/api/update/finish",HTTP_POST,[]{
  if(!updateOwnerAuthorized())return;if(onlineBusy){server.send(409,"text/plain","An online firmware operation is in progress.");return;}if(!transfer.complete()){server.send(409,"text/plain","Upload is incomplete.");return;}
  int result=finalizeTransfer();if(result!=200){server.send(result,"text/plain","Image verification failed. Existing firmware was kept.");return;}
  reply(200,"{\"restarting\":true}");
 });
 server.on("/api/update/abort",HTTP_POST,[]{if(!updateOwnerAuthorized())return;if(onlineBusy){server.send(409,"text/plain","An online firmware operation is in progress.");return;}abortUpdate();reply(200,"{}");});
}
void serviceUpdate(){
 if(transfer.expired(millis())||(transfer.active&&!parentSession.accepts(updateOwner,millis())))abortUpdate();
 if(rebootPending&&!server.sending()&&DragonConnection::elapsed(millis(),rebootAt,1000))ESP.restart();
}
