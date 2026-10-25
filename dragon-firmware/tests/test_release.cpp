#define CONFIG_IDF_TARGET_ESP32S3 1
#include "../DragonPrototype/DragonPrototype.ino"
#include "fakes/WebString.h"
#include "../DragonPrototype/ParentPolicy.h"
#include "../DragonPrototype/UpdatePolicy.h"
#include "../DragonPrototype/BackupPolicy.h"
#include "../DragonPrototype/OnlinePolicy.h"
#include <functional>
#include <cassert>
// Deterministic crypto adapter exercises real route enforcement, not cryptography.
constexpr int MBEDTLS_MD_SHA256=1;
void esp_fill_random(void* p,size_t size){static uint8_t n=0;for(size_t i=0;i<size;i++)((uint8_t*)p)[i]=++n;}
struct esp_partition_t {uint32_t size=0x180000;};
using esp_ota_handle_t=unsigned;using esp_err_t=int;
constexpr int ESP_OK=0,OTA_WITH_SEQUENTIAL_WRITES=-1;
unsigned erases=0,writes=0,aborts=0,bootChanges=0,restarts=0;
esp_partition_t slot;
const esp_partition_t* esp_ota_get_next_update_partition(void*){return &slot;}
int esp_ota_begin(const esp_partition_t*,int,esp_ota_handle_t* handle){erases++;*handle=1;return 0;}
int esp_ota_write(esp_ota_handle_t,const void*,size_t){writes++;return 0;}
int esp_ota_abort(esp_ota_handle_t){aborts++;return 0;}
int esp_ota_end(esp_ota_handle_t){return 0;}
int esp_ota_set_boot_partition(const esp_partition_t*){bootChanges++;return 0;}

struct mbedtls_sha256_context {};
void mbedtls_sha256_init(mbedtls_sha256_context*){}void mbedtls_sha256_free(mbedtls_sha256_context*){}
int mbedtls_sha256_starts(mbedtls_sha256_context*,int){return 0;}int mbedtls_sha256_update(mbedtls_sha256_context*,const uint8_t*,size_t){return 0;}
int mbedtls_sha256_finish(mbedtls_sha256_context*,uint8_t* out){memset(out,0,32);return 0;}
int mbedtls_sha256(const uint8_t*,size_t,uint8_t* out,int){memset(out,0,32);return 0;}
struct mbedtls_pk_context {};
void mbedtls_pk_init(mbedtls_pk_context*){}void mbedtls_pk_free(mbedtls_pk_context*){}
int mbedtls_pk_parse_public_key(mbedtls_pk_context*,const uint8_t*,size_t){return 0;}
int mbedtls_pk_verify(mbedtls_pk_context*,int,const uint8_t*,size_t,const uint8_t* sig,size_t){return sig[0]==42?0:1;}
const char DRAGON_UPDATE_PUBLIC_KEY[]="simulated public key";
constexpr int WL_CONNECTED=3;
struct TestWiFi {int state=WL_CONNECTED;int status(){return state;}} WiFi;
namespace DragonOnline {
struct Transport {
 std::vector<Message> messages;bool active=false;unsigned starts=0;std::string url;
 bool running(){return active;}void cancel(){active=false;messages.clear();}
 bool start(const char* target,uint32_t){url=target;if(active)return false;active=true;starts++;return true;}
 bool read(Message& out){if(messages.empty())return false;out=messages.front();messages.erase(messages.begin());if(out.kind==DONE||out.kind==FAILED)active=false;return true;}
};
}
namespace ParentTest {
constexpr int HTTP_GET=0,HTTP_POST=1;
struct Server {
 std::map<std::pair<std::string,int>,std::function<void()>> routes;
 std::map<std::string,String> fields,headers;int code=0,methodValue=HTTP_POST;String response;
 void on(const char* path,int method,std::function<void()> fn){routes[{path,method}]=fn;}
 String arg(const char* key){return fields[key];}String header(const char* key){return headers[key];}
 int method(){return methodValue;}bool sending(){return false;}
 void send(int status,const char*,const String& text){code=status;response=text;}
 void call(const char* path,int method,std::map<std::string,String> args={}){fields=args;methodValue=method;code=0;routes.at({path,method})();}
} server;
bool authorize(){if(server.method()==HTTP_POST&&server.header("X-Dragon-Request")!="1"){server.send(403,"text/plain","CSRF");return false;}return true;}
void reply(int code,const String& text){server.send(code,"application/json",text);}
String quote(const String& text){return String("\"")+text+"\"";}
#include "../DragonPrototype/ParentWeb.h"
bool numberArgument(const char* key,int low,int high,int& result){String text=server.arg(key);char buf[20];if(text.length()>=sizeof(buf))return false;text.toCharArray(buf,sizeof(buf));return readNumber(buf,low,high,result);}
bool unsignedArgument(const char* key,uint32_t& result){String text=server.arg(key);if(text.empty()||text.length()>10)return false;uint64_t v=0;for(char c:text){if(c<'0'||c>'9')return false;v=v*10+c-'0';}if(v>UINT32_MAX)return false;result=v;return true;}
bool rebootPending=false,connecting=false,joinAfterReply=false,onlineBusy=false,ap=false;
#include "../DragonPrototype/UpdateWeb.h"
#include "../DragonPrototype/OnlineWeb.h"
#include "../DragonPrototype/BackupWeb.h"
}
int main(){
 using namespace ParentTest;
 registerParentRoutes();server.call("/api/parent/login",HTTP_POST,{{"password","dragon123"}});assert(server.code==403);
 server.headers["X-Dragon-Request"]="1";assert(!authorizeParent()&&server.code==401);
 server.call("/api/parent/password",HTTP_POST,{{"password","changedpass"},{"code","dragon123"}});assert(server.code==401);
 assert(storeWrites==0); // Fixed parent access never needs credential setup or storage.
 server.call("/api/parent/login",HTTP_POST,{{"password","badpassword"}});assert(server.code==401);
 server.call("/api/parent/login",HTTP_POST,{{"password","dragon123"}});assert(server.code==429);
 delay(5000);server.call("/api/parent/login",HTTP_POST,{{"password","dragon123"}});assert(server.code==200);
 String token=parentSession.token;server.headers["X-Dragon-Parent"]=token;assert(authorizeParent());
 server.call("/api/parent/password",HTTP_POST,{{"password","changedpass"}});assert(server.code==410&&storeWrites==0);
 server.headers["X-Dragon-Parent"]="wrong";assert(!authorizeParent()&&server.code==401);
 server.headers["X-Dragon-Parent"]=token;delay(DragonParent::SESSION_MS);assert(!authorizeParent());
 // Explicit logout, absolute expiry and rollover.
 delay(5000);server.call("/api/parent/login",HTTP_POST,{{"password","dragon123"}});server.headers["X-Dragon-Parent"]=parentSession.token;
 server.call("/api/parent/logout",HTTP_POST);assert(server.code==200&&!parentSession.token[0]);
 DragonParent::Session wrap;strcpy(wrap.token,std::string(64,'a').c_str());wrap.issued=UINT32_MAX-100;assert(wrap.accepts(wrap.token,100));assert(!wrap.accepts(wrap.token,DragonParent::SESSION_MS));
 DragonUpdate::Transfer update;assert(!update.start(0,0));assert(!update.start(DragonUpdate::MAX_IMAGE+1,0));assert(update.start(1024,0));assert(!update.accepts(1,512));assert(!update.accepts(0,513));assert(update.accepts(0,512));update.offset=512;assert(!update.complete());assert(update.accepts(512,512));update.offset=1024;assert(update.complete());assert(update.expired(30000));
 DragonRotation::State rotation;rotation.settings.enabled=1;rotation.settings.seconds=10;rotation.restart(0);assert(!rotation.due(9999,false));assert(rotation.due(10000,false));assert(!rotation.due(20000,true));assert(!rotation.due(30000,true));assert(!rotation.due(30001,false));assert(rotation.due(40001,false));rotation.restart(45000);assert(!rotation.due(50000,false));
 DragonBackup::Snapshot backup{};DragonLibrary::Library defaults;backup.library=defaults.data;backup.library.checksum=DragonLibrary::checksum(backup.library);backup.check=DragonBackup::checksum(backup);assert(DragonBackup::valid(backup));backup.library.profiles[0].used=0;backup.library.checksum=DragonLibrary::checksum(backup.library);backup.check=DragonBackup::checksum(backup);assert(!DragonBackup::valid(backup));
 // Exercise the real device update and backup handlers with deterministic flash/crypto adapters.
 firmwareValidated=true;registerUpdateRoutes();registerBackupRoutes();
 std::map<std::string,String> manifest={{"format","2"},{"tag","v99.0.0"},{"capabilities","1"},{"schema","1"},{"board","s3"},{"size","512"},{"sha256",String(std::string(64,'0'))},{"signature",String(std::string(512,'0'))}};
 server.headers["X-Dragon-Parent"]="";server.call("/api/update/start",HTTP_POST,manifest);assert(server.code==401&&erases==0);
 randomHex(parentSession.token);parentSession.issued=millis();server.headers["X-Dragon-Parent"]=parentSession.token;
 server.call("/api/update/start",HTTP_POST,manifest);assert(server.code==403&&erases==0); // unsigned rejected BEFORE erase
 manifest["signature"][0]='2';manifest["signature"][1]='a';manifest["board"]="c3";
 server.call("/api/update/start",HTTP_POST,manifest);assert(server.code==400&&erases==0);
 manifest["board"]="s3";
 for(const char* schema:{"","2"}){manifest["schema"]=schema;server.call("/api/update/start",HTTP_POST,manifest);assert(server.code==409&&erases==0);}manifest["schema"]="1";
 voltageCalibrationPresent=true;manifest["capabilities"]="0";server.call("/api/update/start",HTTP_POST,manifest);assert(server.code==409&&erases==0);manifest["capabilities"]="1";voltageCalibrationPresent=false;
 for(const char* tag:{"v0.2.0",DragonOnline::CURRENT_TAG}){manifest["tag"]=tag;server.call("/api/update/start",HTTP_POST,manifest);assert(server.code==409&&erases==0);}manifest["tag"]="v99.0.0";
 manifest["format"]="1";server.call("/api/update/start",HTTP_POST,manifest);assert(server.code==409&&erases==0);manifest["format"]="2";
 server.call("/api/update/start",HTTP_POST,manifest);assert(server.code==200&&erases==1);
 server.call("/api/update/finish",HTTP_POST);assert(server.code==409&&bootChanges==0);
 server.call("/api/update/chunk",HTTP_POST,{{"offset","1"},{"data",String(std::string(1024,'0'))}});assert(server.code==409&&writes==0);
 delay(30000);serviceUpdate();assert(!transfer.active&&aborts==1&&bootChanges==0);
 server.call("/api/update/start",HTTP_POST,manifest);assert(server.code==200);
 server.call("/api/update/chunk",HTTP_POST,{{"offset","0"},{"data",String(std::string(1024,'0'))}});assert(server.code==200&&writes==1);
 auto beforeDuplicate=writes;server.call("/api/update/chunk",HTTP_POST,{{"offset","0"},{"data",String(std::string(1024,'0'))}});assert(server.code==200&&writes==beforeDuplicate);
 server.call("/api/update/chunk",HTTP_POST,{{"offset","0"},{"data",String(std::string(1024,'1'))}});assert(server.code==409&&writes==beforeDuplicate);
 expectedHash[0]=1;server.call("/api/update/finish",HTTP_POST);assert(server.code==403&&bootChanges==0&&!transfer.active);
 server.call("/api/update/start",HTTP_POST,manifest);assert(server.code==200);
 server.call("/api/update/chunk",HTTP_POST,{{"offset","0"},{"data",String(std::string(1024,'0'))}});assert(server.code==200);
 server.call("/api/update/finish",HTTP_POST);assert(server.code==200&&bootChanges==1&&rebootPending);rebootPending=false;
 for(const char* route:{"/api/backup","/api/restore","/api/reset","/api/update/chunk","/api/update/finish","/api/update/abort"}){server.headers["X-Dragon-Parent"]="";server.call(route,!strcmp(route,"/api/backup")?HTTP_GET:HTTP_POST);assert(server.code==401);}
 server.headers["X-Dragon-Parent"]=parentSession.token;
 library.begin();loadLightSettings();loadAlarmSettings();loadRotation();
 auto original=library.data;auto snapshot=makeBackup();assert(DragonBackup::valid(snapshot));
 snapshot.library.profiles[1].used=1;strcpy(snapshot.library.profiles[1].name,"Restored");snapshot.library.checksum=DragonLibrary::checksum(snapshot.library);snapshot.check=DragonBackup::checksum(snapshot);
 assert(queueRestore(snapshot));failStore=true;assert(!recoverRestore());assert(restoreStore.isKey("pending"));assert(!memcmp(&original,&library.data,sizeof(original)));
 failStore=false;assert(recoverRestore());assert(!restoreStore.isKey("pending"));assert(!strcmp(library.data.profiles[1].name,"Restored"));
 // Interrupt each durable record write and retry the original transaction.
 auto calibration=std::vector<unsigned char>{1,2,3,4};otherPreferences["dragon-vcal/unit"]=calibration;
 for(unsigned stage=1;stage<=4;stage++){
  assert(queueRestore(snapshot));failWriteAt=storeWrites+stage;bool completed=recoverRestore();failWriteAt=0;
  if(!completed){assert(restoreStore.isKey("pending"));assert(recoverRestore());}
  assert(otherPreferences["dragon-vcal/unit"]==calibration);
 }
 partialWriteAt=storeWrites+1;auto beforePartial=library.data;assert(!queueRestore(snapshot));partialWriteAt=0;assert(!recoverRestore());assert(restoreStore.isKey("pending"));assert(!memcmp(&beforePartial,&library.data,sizeof(beforePartial)));assert(otherPreferences["dragon-vcal/unit"]==calibration);
 auto rotationWrites=storeWrites;assert(saveRotation(::rotation.settings));assert(storeWrites==rotationWrites);
 restoreStore.bytes("pending")={1,2,3};assert(!recoverRestore());assert(restoreStore.isKey("pending"));
 computerUsbMode=false;serviceRestoreCommand("restore abandon-invalid EVIDENCE-SAVED");assert(restoreStore.isKey("pending"));
 computerUsbMode=true;serviceRestoreCommand("restore abandon-invalid EVIDENCE-SAVED");assert(!restoreStore.isKey("pending"));
 assert(queueRestore(snapshot));failRead=true;serviceRestoreCommand("restore abandon-invalid EVIDENCE-SAVED");failRead=false;assert(restoreStore.isKey("pending"));serviceRestoreCommand("restore abandon-invalid EVIDENCE-SAVED");assert(restoreStore.isKey("pending"));assert(recoverRestore());
 auto after=library.data;server.call("/api/restore",HTTP_POST,{{"data","corrupt"}});assert(server.code==400&&!memcmp(&after,&library.data,sizeof(after)));
 // Actual online API handlers: no network work without parent auth; signed metadata before flash.
 registerOnlineRoutes();simulatedAlarmEpoch=1800000000;
 server.headers["X-Dragon-Parent"]="";server.call("/api/update/online/check",HTTP_POST);assert(server.code==401&&onlineTransport.starts==0);
 server.headers["X-Dragon-Parent"]=parentSession.token;WiFi.state=0;server.call("/api/update/online/check",HTTP_POST);assert(server.code==409);WiFi.state=WL_CONNECTED;
 auto starts=onlineTransport.starts;server.call("/api/update/online/check",HTTP_POST,{{"channel","invalid"}});assert(server.code==400&&onlineTransport.starts==starts);
 auto beforeErase=erases;server.call("/api/update/online/check",HTTP_POST);assert(server.code==202&&onlineBusy&&erases==beforeErase);
 assert(onlineTransport.url.find("/releases/latest/download/")!=std::string::npos);
 auto deliver=[&](const std::string& text){DragonOnline::Message m;m.kind=DragonOnline::DATA;assert(text.size()<=512);m.size=text.size();memcpy(m.bytes,text.data(),m.size);onlineTransport.messages.push_back(m);serviceOnline();};
 auto done=[&](){DragonOnline::Message m;m.kind=DragonOnline::DONE;onlineTransport.messages.push_back(m);serviceOnline();};
 auto metadata=[&](const char* board){return std::string("dragon-update-v2\n")+board+"\nv99.0.0\n512\n"+std::string(64,'0')+"\n1\n1\n2a"+std::string(510,'0')+"\n";};
 deliver("dragon-online-v1\nc3\nv0.3.0\n");done();assert(onlinePhase==ONLINE_FAILED&&onlineMessage.find("No compatible online release")!=std::string::npos&&erases==beforeErase);
 server.call("/api/update/online/check",HTTP_POST);
 auto text=metadata("c3");deliver(text.substr(0,512));deliver(text.substr(512));done();assert(onlinePhase==ONLINE_FAILED&&erases==beforeErase);
 server.call("/api/update/online/check",HTTP_POST);text=metadata("s3");deliver(text.substr(0,512));deliver(text.substr(512));done();assert(onlinePhase==ONLINE_READY&&erases==beforeErase);
 server.call("/api/update/online/install",HTTP_POST,{{"release","v0.3.2"}});assert(server.code==409&&erases==beforeErase);
 server.call("/api/update/online/install",HTTP_POST,{{"release","v99.0.0"}});assert(server.code==202&&erases==beforeErase+1&&onlinePhase==ONLINE_INSTALLING);
 deliver(std::string(512,'x'));auto previousBoot=bootChanges;done();assert(onlinePhase==ONLINE_RESTARTING&&bootChanges==previousBoot+1&&rebootPending);rebootPending=false;
 server.call("/api/update/online/check",HTTP_POST);text=metadata("s3");deliver(text.substr(0,512));deliver(text.substr(512));done();server.call("/api/update/online/install",HTTP_POST,{{"release","v99.0.0"}});auto previousAbort=aborts;parentSession.clear();serviceOnline();assert(onlinePhase==ONLINE_FAILED&&!transfer.active&&aborts==previousAbort+1);
 parentSession.issued=millis();memset(parentSession.token,'b',64);parentSession.token[64]=0;server.headers["X-Dragon-Parent"]=parentSession.token;
 server.call("/api/update/online/check",HTTP_POST,{{"channel","beta"}});assert(server.code==202&&onlineTransport.url.find("/download/firmware-beta/dragon-s3.manifest")!=std::string::npos);
 text=metadata("s3");deliver(text.substr(0,512));deliver(text.substr(512));done();assert(onlinePhase==ONLINE_FAILED); // stable metadata cannot be offered as beta
 server.call("/api/update/online/check",HTTP_POST,{{"channel","beta"}});text=metadata("s3");text.replace(text.find("v99.0.0"),7,"v99.0.0-beta.1");deliver(text.substr(0,512));deliver(text.substr(512));done();assert(onlinePhase==ONLINE_READY);
 server.call("/api/update/online/check",HTTP_POST);assert(onlineChannel=="release");deliver(text.substr(0,512));deliver(text.substr(512));done();assert(onlinePhase==ONLINE_FAILED); // beta must never leak into default release channel
 assert(DragonOnline::allowedURL("https://github.com/sai021/dragon-kingdom/releases/latest/download/dragon-s3.manifest"));assert(!DragonOnline::allowedURL("http://github.com/a"));assert(!DragonOnline::allowedURL("https://github.com.evil.test/a"));assert(!DragonOnline::allowedURL("https://github.com@evil.test/a"));
 puts("PASS: actual fixed-password parent API CSRF/login/throttle/token/expiry/logout/retired-change-route, update bounds/interruption, rotation pause/manual interval and backup validation. Crypto adapter is simulated.");
}
