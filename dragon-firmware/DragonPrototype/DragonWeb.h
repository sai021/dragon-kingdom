#pragma once
#include <WiFi.h>
#include "BoundedWebServer.h"
#include <DNSServer.h>
#include <ESPmDNS.h>
#include <esp_system.h>
#include "ConnectionPolicy.h"
#include "NetworkSerial.h"
#include "ParentPolicy.h"
#include <mbedtls/md.h>
#include <mbedtls/pk.h>
#include <mbedtls/sha256.h>
#include <esp_ota_ops.h>
#include "UpdatePolicy.h"
#include "BackupPolicy.h"
#include "UpdatePublicKey.h"
#include "OnlineTransport.h"

// Included after lighting functions so web and touch share the same state.
namespace DragonWeb {
BoundedWebServer server(80);
DNSServer dns;
Preferences store;
struct Credentials { char ssid[33]; char password[65]; } saved{}, pending{};
String deviceName, password, message="Ready to play";
bool ap=false, connecting=false, configured=false, ready=false;
bool scanRequested=false,joinAfterReply=false,forgetAfterReply=false;
bool lastJoinSaved=false,joinedSession=false,rebootPending=false,onlineBusy=false;
uint32_t joinedAt=0;
DragonConnection::Reconnect reconnect;
bool stationOnline=false,reconnecting=false;
IPAddress mdnsAddress;
volatile uint16_t lastDisconnectReason=0;
uint32_t started=0, retryAt=0, apActivity=0;
#include "DragonWebPage.h"
static_assert(sizeof(page)+1024<=DragonHttp::MAX_RESPONSE,"Embedded page exceeds the bounded HTTP response capacity.");
String quote(const String& value){String out="\"";for(size_t i=0;i<value.length();i++){char c=value[i];if(c=='"'||c=='\\'){out+='\\';out+=c;}else if(uint8_t(c)<32){char escape[7];snprintf(escape,sizeof(escape),"\\u%04x",uint8_t(c));out+=escape;}else out+=c;}return out+'"';}
bool authorize(){if(rebootPending&&server.method()==HTTP_POST){server.send(409,"text/plain","Restart pending. Reconnect after startup.");return false;}if(server.method()==HTTP_POST&&server.header("X-Dragon-Request")!="1"){server.send(403,"text/plain","Open the Dragon Kingdom to make changes.");return false;}server.sendHeader("Cache-Control","no-store");return true;}
void reply(int code,const String& text){server.send(code,"application/json",text);}
bool openAP(){if(ap)return true;if(joinedSession){message="Power cycle to open setup Wi-Fi.";return false;}WiFi.mode(WIFI_AP_STA);if(!WiFi.softAP(deviceName.c_str(),password.c_str())){message="Could not start setup Wi-Fi. Restart your dragon.";return false;}ap=true;apActivity=millis();dns.start(53,"*",WiFi.softAPIP());return true;}
void connect(const Credentials& credentials,bool retry=false){
 reconnecting=retry;
 if(joinedSession&&!retry){message="Power cycle to try home Wi-Fi again.";return;}
 lastJoinSaved=false;
 // Stop the responder before destroying/recreating its station interface.
 MDNS.end();
 // disconnect() is a no-op while disconnected in Arduino ESP32 3.2.1,
 // even if the driver is still associating. Stop STA before replacing its
 // configuration; keep the setup AP and all saved credentials intact.
 WiFi.setAutoReconnect(false);
 WiFi.enableSTA(false);
 // STA.begin(false) waits for the asynchronous START event in the pinned core.
 // enableSTA(true) alone can return before setTxPower() is permitted.
 if(!WiFi.STA.begin(false)){connecting=false;message="Could not start home Wi-Fi. Try again.";retryAt=millis();return;}
 WiFi.setHostname(deviceName.c_str());
 // Apply the tested radio limit before any association frames are sent.
 if(!WiFi.setTxPower(wifi_power_t(Config::WIFI_TX_QUARTER_DBM))){
  WiFi.enableSTA(false);connecting=false;message="Could not apply Wi-Fi power limit. Try again.";retryAt=millis();return;
 }
 auto result=WiFi.begin(credentials.ssid,credentials.password);
 started=millis();connecting=result!=WL_CONNECT_FAILED;
 if(!connecting){message="Could not start home Wi-Fi. Try again.";retryAt=started;}
}
bool authorizeParent();
#include "ParentWeb.h"
bool serviceRestoreCommand(const char* line);
bool firmwareOperationBusy();
bool serialControl(char* line){
 if(serviceRestoreCommand(line))return true;

 if(strncmp(line,"wifi ",5))return false;
 char* context=nullptr;char* action=strtok_r(line+5," ", &context);
 if(!ready&&action&&strcmp(action,"status")){Serial.println("network_unavailable reason=power_or_storage");return true;}
 if(action&&!strcmp(action,"setup")){
  Serial.printf("network_setup opened=%u\n",ready&&openAP());return true;
 }
 if(action&&!strcmp(action,"sleep")){
  char* value=strtok_r(nullptr," ",&context);
  if(!value||(strcmp(value,"on")&&strcmp(value,"off"))){Serial.println("Wi-Fi sleep command: on or off.");return true;}
  bool changed=WiFi.setSleep(!strcmp(value,"on"));
  Serial.printf("network_power_save changed=%u mode=%u\n",changed,unsigned(WiFi.getSleep()));return true;
 }
 if(action&&!strcmp(action,"status")){
  Serial.printf("network_status connected=%u configured=%u access_point=%u ip=%s hostname=%s.local status=%u disconnect_reason=%u rssi=%d joining=%u join_saved=%u tx_quarter_dbm=%d sta_started=%u\n",
   WiFi.status()==WL_CONNECTED,configured,ap,WiFi.localIP().toString().c_str(),deviceName.c_str(),
   unsigned(WiFi.status()),unsigned(lastDisconnectReason),WiFi.RSSI(),connecting,lastJoinSaved,
   int(WiFi.getTxPower()),WiFi.STA.started());return true;
 }
 if(action&&!strcmp(action,"scan")){
  if(firmwareOperationBusy()){Serial.println("network_scan busy=1");return true;}
  int count=WiFi.scanComplete();
  if(connecting){Serial.println("network_scan busy=1");return true;}
  if(!scanRequested){WiFi.scanDelete();scanRequested=true;WiFi.scanNetworks(true);Serial.println("network_scan scanning=1");return true;}
  if(count==WIFI_SCAN_RUNNING){Serial.println("network_scan scanning=1");return true;}
  Serial.printf("network_scan count=%d\n",count);
  for(int i=0;i<count&&i<32;i++){
   String name=WiFi.SSID(i);Serial.print("network_found name_hex=");
   for(size_t j=0;j<name.length();j++)Serial.printf("%02x",uint8_t(name[j]));
   Serial.printf(" rssi=%d channel=%d encryption=%u\n",WiFi.RSSI(i),WiFi.channel(i),unsigned(WiFi.encryptionType(i)));
  }
  scanRequested=false;WiFi.scanDelete();return true;
 }
 if(action&&!strcmp(action,"join")){
  char* ssid=strtok_r(nullptr," ",&context);char* key=strtok_r(nullptr," ",&context);
  Credentials candidate{};
  if(!ssid||!key||strtok_r(nullptr," ",&context)||
     !DragonNetworkSerial::decode(ssid,candidate.ssid,sizeof(candidate.ssid))||!candidate.ssid[0]||
     (strcmp(key,"-")&&!DragonNetworkSerial::decode(key,candidate.password,sizeof(candidate.password)))||
     !DragonNetworkSerial::validPassword(candidate.password)){
   Serial.println("Wi-Fi request rejected: invalid credentials.");return true;
  }
  if(firmwareOperationBusy()||!ready||connecting||joinAfterReply||forgetAfterReply||WiFi.scanComplete()==WIFI_SCAN_RUNNING){Serial.println("Wi-Fi request rejected: networking busy or unavailable.");return true;}
  pending=candidate;message="Trying home Wi-Fiâ€¦";
  Serial.println("Wi-Fi request accepted; credentials are not echoed.");
  connect(pending);return true;
 }
 Serial.println("Wi-Fi command: setup, status, scan or join HEX_SSID HEX_PASSWORD (use - for an open network).");return true;
}
#include "LibraryWeb.h"
#include "AlarmWeb.h"
#include "UpdateWeb.h"
#include "OnlineWeb.h"
#include "BackupWeb.h"
bool firmwareOperationBusy(){return onlineBusy||transfer.active||rebootPending;}
void begin(bool requested){
 ready=store.begin("dragon-wifi",false);if(!ready){Serial.println("Wi-Fi storage unavailable; networking disabled");return;}
 char suffix[7];snprintf(suffix,sizeof(suffix),"%06lx",(unsigned long)DragonConnection::deviceSuffix(ESP.getEfuseMac()));deviceName=String("Dragon-Kingdom-")+suffix;
 // Shared, easy-to-type setup password, including migration from older random keys.
 // Only the device access key changes; saved home Wi-Fi and library data remain intact.
 password="dragon123";if(store.getString("access","")!=password){if(store.putString("access",password)!=password.length()){ready=false;return;}}
 if(store.getBytesLength("home")==sizeof(saved)&&store.getBytes("home",&saved,sizeof(saved))==sizeof(saved)&&memchr(saved.ssid,0,sizeof(saved.ssid))&&memchr(saved.password,0,sizeof(saved.password))&&saved.ssid[0])configured=true;
 // connect()/openAP() starts the required interface once. Starting STA here
 // would immediately tear it down again in connect() on every saved-network
 // boot, needlessly cycling the pinned core's asynchronous event/netif setup.
 WiFi.persistent(false);WiFi.setHostname(deviceName.c_str());WiFi.setAutoReconnect(false);
 WiFi.onEvent([](arduino_event_id_t event,arduino_event_info_t info){
  if(event==ARDUINO_EVENT_WIFI_STA_DISCONNECTED)lastDisconnectReason=info.wifi_sta_disconnected.reason;
 });
 // UTC only; the phone supplies actual local timezone/DST transition rules.
 configTime(0,0,"pool.ntp.org","time.cloudflare.com");
 openAP();if(configured)connect(saved);
 Serial.printf("Dragon web: network=%s password=%s setup=http://192.168.4.1 home=http://%s.local\n",deviceName.c_str(),password.c_str(),deviceName.c_str());
 server.on("/",HTTP_GET,[]{if(authorize()){if(server.header("Accept-Encoding").indexOf("gzip")>=0){server.sendHeader("Content-Encoding","gzip");server.sendHeader("Vary","Accept-Encoding");server.send_P(200,"text/html",reinterpret_cast<const char*>(pageGzip),sizeof(pageGzip));}else server.send_P(200,"text/html",page);}});
 server.on("/api/state",HTTP_GET,[]{if(!authorize())return;bool online=WiFi.status()==WL_CONNECTED;reply(200,String("{\"firmware\":")+quote(DragonOnline::CURRENT_TAG)+",\"board\":"+quote(boardName())+",\"connected\":"+(online?"true":"false")+",\"accessPoint\":"+(ap?"true":"false")+",\"connecting\":"+(connecting?"true":"false")+",\"mode\":"+String(unsigned(mode))+",\"hostname\":"+quote(deviceName)+",\"ip\":"+quote(WiFi.localIP().toString())+",\"message\":"+quote(message)+",\"dragon\":"+String(palette)+",\"profile\":"+String(library.data.active)+",\"brightness\":"+String(brightness)+"}");});
 server.on("/api/dragons",HTTP_GET,[]{if(!authorize())return;String out="[";unsigned added=0;for(int i=0;i<PRESET_COUNT+DragonLibrary::CUSTOM_LIMIT;i++){if(!(server.arg("catalog")=="1"?DragonLibrary::selectable(library.data,i,library.data.active):DragonLibrary::contains(library.data,i,library.data.active)))continue;if(added++)out+=',';auto p=library.resolve(i);out+="{\"id\":"+String(i)+",\"name\":"+quote(p.name)+",\"custom\":"+(i>=PRESET_COUNT?"true":"false")+",\"owned\":"+(i>=PRESET_COUNT&&library.data.customs[i-PRESET_COUNT].owner==library.data.active?"true":"false")+"}";}reply(200,out+"]");});
 server.on("/api/support",HTTP_GET,[]{
  if(!authorizeParent())return;
  const auto* running=esp_ota_get_running_partition();esp_ota_img_states_t state=ESP_OTA_IMG_UNDEFINED;if(running)esp_ota_get_state_partition(running,&state);
  reply(200,String("{\"firmware\":")+quote(DragonOnline::CURRENT_TAG)+",\"board\":"+quote(boardName())+",\"uptimeMs\":"+String(millis())+",\"resetReason\":"+String(unsigned(esp_reset_reason()))+",\"otaState\":"+String(unsigned(state))+",\"validated\":"+(firmwareValidated?"true":"false")+",\"validationReason\":"+quote(bootValidation.reason)+",\"startupResult\":"+quote(startupResult)+",\"estimatedCeilingMa\":"+String(operatingTotal)+",\"calibrationPresent\":"+(voltageCalibrationPresent?"true":"false")+",\"connected\":"+(WiFi.status()==WL_CONNECTED?"true":"false")+",\"disconnectReason\":"+String(lastDisconnectReason)+",\"freeHeap\":"+String(ESP.getFreeHeap())+",\"minimumHeap\":"+String(ESP.getMinFreeHeap())+",\"largestHeapBlock\":"+String(ESP.getMaxAllocHeap())+"}");
 });
 registerParentRoutes();
 registerLibraryRoutes();
 registerAlarmRoutes();
 registerUpdateRoutes();
 registerOnlineRoutes();
 registerBackupRoutes();
 server.on("/api/scan",HTTP_POST,[]{
  if(!authorizeParent())return;
  if(onlineBusy||transfer.active){server.send(409,"text/plain","Wait for the firmware operation to finish.");return;}
  if(connecting){server.send(409,"text/plain","Wait for the Wi-Fi connection attempt to finish.");return;}
  if(WiFi.scanComplete()==WIFI_SCAN_RUNNING){reply(202,"{}");return;}
  WiFi.scanDelete();scanRequested=true;
  int result=WiFi.scanNetworks(true);
  if(result==WIFI_SCAN_FAILED){scanRequested=false;server.send(503,"text/plain","Could not look for networks. You can enter the name yourself.");return;}
  reply(202,"{}");
 });
 server.on("/api/scan",HTTP_GET,[]{
  if(!authorizeParent())return;
  int count=WiFi.scanComplete();
  if(!scanRequested){reply(200,"{\"scanning\":false,\"networks\":[]}");return;}
  if(count==WIFI_SCAN_RUNNING){reply(200,"{\"scanning\":true,\"networks\":[]}");return;}
  if(count<0){server.send(503,"text/plain","Could not look for networks. You can enter the name yourself.");return;}
  String data="{\"scanning\":false,\"networks\":[";unsigned added=0;
  for(int i=0;i<count&&added<32;i++){
   String name=WiFi.SSID(i);if(!name.length()||name==deviceName)continue;
   bool duplicate=false;for(int j=0;j<i;j++)if(WiFi.SSID(j)==name){duplicate=true;break;}
   if(duplicate)continue;if(added++)data+=',';
   data+="{\"name\":"+quote(name)+",\"open\":"+(WiFi.encryptionType(i)==WIFI_AUTH_OPEN?"true":"false")+"}";
  }
  reply(200,data+"]}");
 });
 server.on("/api/wifi",HTTP_POST,[]{if(!authorizeParent())return;if(onlineBusy||transfer.active){server.send(409,"text/plain","Wait for the firmware operation to finish.");return;}if(joinedSession){server.send(409,"text/plain","Power cycle before changing Wi-Fi. The dragon network opens at every startup.");return;}if(WiFi.scanComplete()==WIFI_SCAN_RUNNING){server.send(409,"text/plain","Wait for the Wi-Fi search to finish.");return;}if(connecting){server.send(409,"text/plain","Already trying Wi-Fi. Please wait.");return;}String ssid=server.arg("ssid"),key=server.arg("password");bool validKey=key.length()==0||(key.length()>=8&&key.length()<=63);if(key.length()==64){validKey=true;for(size_t i=0;i<64;i++)if(!isxdigit(key[i]))validKey=false;}if(!ssid.length()||ssid.length()>32||!validKey){server.send(400,"text/plain","Check the Wi-Fi name and password length.");return;}pending={};ssid.toCharArray(pending.ssid,sizeof(pending.ssid));key.toCharArray(pending.password,sizeof(pending.password));message="Trying home Wi-Fiâ€¦";reply(202,"{}");joinAfterReply=true;});
 server.on("/api/wifi/retry",HTTP_POST,[]{if(!authorizeParent())return;if(onlineBusy||transfer.active||joinedSession||connecting||!configured||WiFi.scanComplete()==WIFI_SCAN_RUNNING){server.send(409,"text/plain","Retry is available after a failed join with saved Wi-Fi. Power cycle after a successful session.");return;}pending=saved;joinAfterReply=true;message="Trying saved home Wi-Fi. Your phone may briefly disconnect while the radio changes channel.";reply(202,"{}");});
 server.on("/api/play",HTTP_POST,[]{if(!authorize())return;if(!DragonLibrary::contains(library.data,library.next(255),library.data.active)){server.send(409,"text/plain","Add favourites or make a dragon for this profile first.");return;}String action=server.arg("action"),value=server.arg("value");bool ok=false;int number=0;char buffer[16];value.toCharArray(buffer,sizeof(buffer));if(action=="dragon"&&value.length()<sizeof(buffer)&&readNumber(buffer,0,PRESET_COUNT+DragonLibrary::CUSTOM_LIMIT-1,number)&&DragonLibrary::contains(library.data,number,library.data.active)){if(mode==OFF||!brightness)wakeLighting();setPalette(number);mode=ZONE_VIEW;ok=true;}else if(action=="brightness"&&value.length()<sizeof(buffer)&&readNumber(buffer,0,100,number)){if(number&&mode==OFF)wakeLighting();setBrightness(number);ok=true;}else if(action=="toggle"){toggleLighting();ok=true;}else if(action=="effect"){const char* names[]={"zones","breathe","colorcycle","glitter","incendio","leviosa"};for(int i=0;i<6;i++)if(value==names[i]){if(mode==OFF||!brightness)wakeLighting();mode=Mode(i);ok=true;}}if(ok){rawGlowTest=0;sunrise.stop();rememberLighting();reply(200,"{}");}else server.send(400,"text/plain","Unknown dragon control.");});
 server.on("/api/forget-wifi",HTTP_POST,[]{
  if(!authorizeParent())return;
  if(onlineBusy||transfer.active){server.send(409,"text/plain","Wait for the firmware operation to finish.");return;}
  if(store.isKey("home")&&!store.remove("home")){server.send(500,"text/plain","Could not forget Wi-Fi. Try again.");return;}
  configured=false;connecting=false;saved={};pending={};
  message="Home Wi-Fi forgotten. Power cycle to open the dragon network.";
  reply(200,"{}");forgetAfterReply=true;
 });
 const char* headers[]={"X-Dragon-Request","X-Dragon-Parent","Accept-Encoding"};server.collectHeaders(headers,3);
 server.onNotFound([]{server.sendHeader("Location",ap?"http://192.168.4.1/":"/");server.send(302,"text/plain","");});server.begin();
}
void update(uint32_t now){if(!ready)return;server.handleClient();serviceOnline();serviceUpdate();if(ap)dns.processNextRequest();
 // Requests can start timers after the caller sampled now. Refresh before
 // unsigned elapsed checks, or a new attempt can appear 49 days overdue.
 now=millis();
 // Finish queuing the reply before changing the station interface it uses.
 if(!server.sending()&&forgetAfterReply){
  forgetAfterReply=false;joinAfterReply=false;MDNS.end();WiFi.setAutoReconnect(false);WiFi.enableSTA(false);
 }
 if(!server.sending()&&joinAfterReply){joinAfterReply=false;connect(pending);now=millis();}
 if(DragonConnection::joinedExpectedNetwork(WiFi.status()==WL_CONNECTED,connecting,pending.ssid[0],String(pending.ssid)==WiFi.SSID())){connecting=false;stationOnline=true;reconnect.joined();if(!joinedSession)joinedAt=now;joinedSession=true;WiFi.setAutoReconnect(false);if(pending.ssid[0]&&!reconnecting){if(store.putBytes("home",&pending,sizeof(pending))==sizeof(pending)){saved=pending;configured=true;lastJoinSaved=true;message="Home Wi-Fi saved";}else message="Connected, but settings could not be saved. Try again.";pending={};}else {pending={};message="Ready to play";}reconnecting=false;mdnsAddress=WiFi.localIP();MDNS.end();MDNS.begin(deviceName.c_str());MDNS.addService("http","tcp",80);retryAt=now;}
 if(connecting&&DragonConnection::elapsed(now,started,DragonConnection::CONNECT_TIMEOUT_MS)){MDNS.end();WiFi.setAutoReconnect(false);WiFi.enableSTA(false);pending={};connecting=false;message="Could not join home Wi-Fi. Check the name and password, then try again.";retryAt=now;if(reconnecting){reconnect.failed(now);reconnecting=false;}}
 if(joinedSession&&configured&&!connecting){
  bool online=WiFi.status()==WL_CONNECTED;
  if(stationOnline&&!online){stationOnline=false;MDNS.end();reconnect.lost(now);message="Home Wi-Fi disconnected; retrying automatically.";}
  if(online&&(!stationOnline||mdnsAddress!=WiFi.localIP())){stationOnline=true;reconnect.joined();mdnsAddress=WiFi.localIP();MDNS.end();MDNS.begin(deviceName.c_str());MDNS.addService("http","tcp",80);}
  bool busy=server.sending()||joinAfterReply||forgetAfterReply||onlineBusy||transfer.active||rebootPending||WiFi.scanComplete()==WIFI_SCAN_RUNNING;
  if(reconnect.due(now,busy)){pending=saved;connect(saved,true);if(!connecting)reconnect.failed(millis());}
 }
 if(ap&&DragonConnection::closeAccessPoint(joinedSession,connecting,WiFi.softAPgetStationNum(),millis(),joinedAt)&&!server.sending()){dns.stop();WiFi.softAPdisconnect(true);WiFi.mode(WIFI_STA);ap=false;}
}
}
