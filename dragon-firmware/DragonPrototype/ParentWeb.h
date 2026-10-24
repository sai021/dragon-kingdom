#pragma once
// Included inside DragonWeb. This shared password is a deliberate-action gate.
// It is independent of saved user data and requires no setup, USB code or change.
DragonParent::Session parentSession;
bool loginCooling=false;
uint32_t loginAttempt=0;
void randomHex(char* out){uint8_t bytes[32];esp_fill_random(bytes,sizeof(bytes));for(unsigned i=0;i<32;i++)sprintf(out+i*2,"%02x",bytes[i]);}
bool authorizeParent(){
 if(!authorize())return false;
 if(!parentSession.accepts(server.header("X-Dragon-Parent").c_str(),millis())){server.send(401,"text/plain","Enter the parent password to unlock settings.");return false;}
 return true;
}
void registerParentRoutes(){
 server.on("/api/parent",HTTP_GET,[]{if(!authorize())return;reply(200,String("{\"configured\":true,\"unlocked\":")+(parentSession.accepts(server.header("X-Dragon-Parent").c_str(),millis())?"true":"false")+"}");});
 server.on("/api/parent/login",HTTP_POST,[]{
  if(!authorize())return;uint32_t now=millis();
  if(loginCooling&&DragonParent::live(now,loginAttempt,DragonParent::COOLDOWN_MS)){server.send(429,"text/plain","Wait five seconds before trying again.");return;}
  loginCooling=true;loginAttempt=now;String key=server.arg("password");
  if(key.length()!=strlen(DragonParent::PASSWORD)||!DragonParent::equal((const uint8_t*)key.c_str(),(const uint8_t*)DragonParent::PASSWORD,key.length())){server.send(401,"text/plain","Parent password did not match.");return;}
  randomHex(parentSession.token);parentSession.issued=millis();reply(200,String("{\"token\":")+quote(parentSession.token)+"}");
 });
 // A cached older page must not offer a working password-change/setup route.
 server.on("/api/parent/password",HTTP_POST,[]{if(!authorizeParent())return;server.send(410,"text/plain","The parent password stays dragon123. No setup or password change is needed.");});
 server.on("/api/parent/logout",HTTP_POST,[]{if(!authorizeParent())return;parentSession.clear();reply(200,"{}");});
}
