#define CONFIG_IDF_TARGET_ESP32S3 1
#include "../DragonPrototype/DragonPrototype.ino"
#include "fakes/WebString.h"
#include <map>
#include <functional>
#include <cassert>
namespace AuditWeb {
constexpr int HTTP_GET=0,HTTP_POST=1;
struct FakeServer {
 std::map<std::pair<std::string,int>,std::function<void()>> handlers;
 std::map<std::string,String> args;int code=0;String response;
 void on(const char* path,int method,std::function<void()> fn){handlers[{path,method}]=fn;}
 String arg(const char* key){return args[key];}
 void send(int status,const char*,const String& text){code=status;response=text;}
 void post(const char* path,std::map<std::string,String> fields){args=fields;code=0;handlers.at({path,HTTP_POST})();}
} server;
bool authorize(){return true;}
void reply(int code,const String& text){server.send(code,"application/json",text);}
String quote(const String& value){return String("\"")+value+"\"";}
#include "../DragonPrototype/LibraryWeb.h"
}
int main(){
 assert(library.begin());auto candidate=library.data;
 for(int i=1;i<=2;i++){auto& p=candidate.profiles[i];p.used=1;strcpy(p.name,i==1?"Child A":"Child B");p.count=1;p.favorites[0]=i;}
 candidate.active=1;assert(library.save(candidate));AuditWeb::registerLibraryRoutes();
 auto original=library.data;
 auto post=[&](const char* path,std::map<std::string,String> args,int status){AuditWeb::server.post(path,args);assert(AuditWeb::server.code==status);};
 post("/api/profile",{{"action","select"},{"id","2"},{"profile","1"},{"generation",String(original.generation)}},200);
 auto switched=library.data;
 post("/api/profile",{{"action","update"},{"name","Stale"},{"brightness","80"},{"favorites","0"},{"profile","1"},{"generation",String(original.generation)}},409);
 assert(!memcmp(&switched,&library.data,sizeof(switched)));
 for(const char* route:{"/api/profile","/api/custom","/api/delete-custom","/api/delete-profile"}){
  post(route,{},409);assert(!memcmp(&switched,&library.data,sizeof(switched)));
  for(const char* bad:{"-1","4294967296","18446744073709551616","1x",""}){
   post(route,{{"profile","2"},{"generation",bad}},409);assert(!memcmp(&switched,&library.data,sizeof(switched)));
  }
 }
 post("/api/profile",{{"action","update"},{"name","Child B edited"},{"brightness","80"},{"favorites","0"},{"profile","2"},{"generation",String(switched.generation)}},200);
 assert(!strcmp(library.data.profiles[1].name,"Child A"));assert(!strcmp(library.data.profiles[2].name,"Child B edited"));
 auto fresh=library.data;
 std::map<std::string,String> custom={{"profile","2"},{"generation",String(fresh.generation)},{"id","-1"},{"base","0"},{"colorMask","0"},{"name","My creation"},{"colors",String(std::string(60,'0'))},{"effectZones","0,0,0,0"}};
 post("/api/custom",custom,200);assert(library.data.customs[0].owner==2);
 auto created=library.data;post("/api/custom",custom,409);assert(!memcmp(&created,&library.data,sizeof(created))); // Lost-response retry cannot duplicate.
 post("/api/delete-custom",{{"id",String(PRESET_COUNT)},{"profile","2"},{"generation",String(created.generation)}},200);
 assert(!library.data.customs[0].used);
 auto beforeDelete=library.data;
 post("/api/delete-profile",{{"id","0"},{"profile","2"},{"generation",String(beforeDelete.generation)}},403);
 assert(library.data.profiles[0].used&&!strcmp(library.data.profiles[0].name,"All"));
 post("/api/delete-profile",{{"id","2"},{"profile","2"},{"generation",String(beforeDelete.generation)}},200);
 assert(library.data.active==0&&!library.data.profiles[2].used);
 // A wrapped generation value of zero must remain a valid request context.
 library.data.generation=0;
 post("/api/profile",{{"action","select"},{"id","1"},{"profile","0"},{"generation","0"}},200);
 puts("PASS: actual library routes reject stale/missing/malformed contexts, preserve All and reject duplicate create retries; valid save/delete and generation rollover work.");
}
