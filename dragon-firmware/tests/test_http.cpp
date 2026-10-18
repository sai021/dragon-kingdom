#include "../DragonPrototype/BoundedWebServer.h"
#include <cassert>
#include <cstdio>
using namespace DragonHttp;
Result inspect(const std::string& value){return DragonHttp::inspect(value.data(),value.size());}
int main(){
 const std::string get="GET /api/state HTTP/1.1\r\nHost: dragon\r\n\r\n";
 assert(inspect(get)==READY);
 const std::string post="POST /api/play HTTP/1.1\r\nContent-Type: application/x-www-form-urlencoded;charset=UTF-8\r\nContent-Length: 3\r\n\r\na=1";
 for(size_t i=0;i<post.size();i++)assert(DragonHttp::inspect(post.data(),i)==WAIT);
 assert(inspect(post)==READY);
 BufferedRequestClient memory(post.data(),post.size());assert(memory.peek()=='P'&&memory.available()==int(post.size()));
 char copied[5];assert(memory.readBytes(copied,sizeof(copied))==sizeof(copied));assert(std::string(copied,5)=="POST ");
 const std::string maximum="POST /api/custom HTTP/1.1\r\nContent-Type: application/x-www-form-urlencoded\r\nContent-Length: "+std::to_string(MAX_BODY)+"\r\n\r\n"+std::string(MAX_BODY,'x');
 assert(inspect(maximum)==READY);
 for(auto value:{"GET / HTTP/1.1\r\nContent-Length: 1\r\n\r\na",
  "POST / HTTP/1.1\r\nContent-Length: 999999999999999999999\r\n\r\n",
  "POST / HTTP/1.1\r\nContent-Length: 0\r\nContent-Length: 0\r\n\r\n",
  "POST / HTTP/1.1\r\nTransfer-Encoding: chunked\r\n\r\n",
  "POST / HTTP/1.1\r\nExpect: 100-continue\r\nContent-Length: 3\r\n\r\n",
  "POST / HTTP/1.1\r\nContent-Type: multipart/form-data\r\nContent-Length: 3\r\n\r\na=1",
  "POST / HTTP/1.1\r\n\r\n", "GET / HTTP/1.1\r\nBad-header\r\n\r\n"})assert(inspect(std::string(value))==REJECT);
 assert(inspect(get+get)==REJECT);
 auto nul=get;nul[3]=0;assert(inspect(nul)==REJECT);
 assert(inspect(std::string(MAX_HEADERS,'x'))==REJECT);
 BoundedWebServer server(80);fakeTime=0;
 auto slow=std::make_shared<HttpPeer>();slow->input="GET /";server.acceptPeer(slow);server.handleClient();
 for(unsigned i=1;i<REQUEST_MS;i++){fakeTime=i;if(i%100==0)slow->input+='x';server.handleClient();assert(httpHandled==0);}
 fakeTime=REQUEST_MS;server.handleClient();assert(!slow->connected&&httpHandled==0);
 auto normal=std::make_shared<HttpPeer>();normal->input=post;normal->writeLimit=7;server.acceptPeer(normal);server.handleClient();assert(httpHandled==1&&server.sending());
 for(unsigned i=0;i<100&&server.sending();i++){fakeTime++;server.handleClient();}
 assert(normal->output==httpResponse&&!server.sending());
 auto fragments=std::make_shared<HttpPeer>();fragments->input=post;fragments->readLimit=3;server.acceptPeer(fragments);
 auto handled=httpHandled;for(size_t i=0;i<post.size();i++){fakeTime++;server.handleClient();}
 assert(httpHandled==handled+1&&httpParsed==post);
 while(server.sending()){fakeTime++;server.handleClient();}
 assert(fragments->output==httpResponse);
 auto full=std::make_shared<HttpPeer>();full->input=maximum;server.acceptPeer(full);handled=httpHandled;
 for(unsigned i=0;i<10;i++){fakeTime++;server.handleClient();}
 assert(httpHandled==handled+1&&httpParsed==maximum);
 while(server.sending()){fakeTime++;server.handleClient();}
 auto blocked=std::make_shared<HttpPeer>();blocked->input=get;blocked->blocked=true;server.acceptPeer(blocked);server.handleClient();
 auto started=fakeTime;for(unsigned i=0;i<RESPONSE_MS;i+=100){fakeTime=started+i;server.handleClient();assert(server.sending());}
 fakeTime=started+RESPONSE_MS;server.handleClient();assert(!blocked->connected&&!server.sending());
 auto large=std::make_shared<HttpPeer>();large->input=get;server.acceptPeer(large);httpResponse.assign(MAX_RESPONSE+1,'x');server.handleClient();assert(!large->connected&&!server.sending());
 auto disconnected=std::make_shared<HttpPeer>();disconnected->input="GET /";server.acceptPeer(disconnected);server.handleClient();disconnected->connected=false;server.handleClient();
 // Whole-request deadline remains correct across millis rollover.
 fakeTime=0xfffffff0u;auto wrap=std::make_shared<HttpPeer>();wrap->input="GET /";server.acceptPeer(wrap);server.handleClient();
 fakeTime+=REQUEST_MS;server.handleClient();assert(!wrap->connected);
 puts("PASS: bounded HTTP framing, partial/trickling/oversized requests, duplicate length, slow responses, short writes, disconnects and timer rollover.");
}
