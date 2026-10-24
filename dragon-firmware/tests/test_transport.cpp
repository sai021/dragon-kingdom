// Actual transport adapter against a deterministic HTTP/RTOS fixture; no TLS crypto.
#include "../DragonPrototype/OnlineTransport.h"
#include <cassert>
int main(){
 using namespace DragonOnline;
 Transport transport;Message message;
 redirectURL="https://release-assets.githubusercontent.com/release/file?token="+std::string(850,'x');
 assert(redirectURL.size()>512&&redirectURL.size()<URL_CAPACITY);
 assert(transport.start("https://github.com/owner/project/releases/latest/download/test.manifest",1024));worker();
 assert(opens==2&&cleanups==2);assert(transport.read(message)&&message.kind==DATA);assert(transport.read(message)&&message.kind==DONE);assert(!transport.read(message));
 // Oversized redirects fail explicitly; no truncated signed address is requested.
 redirectURL="https://release-assets.githubusercontent.com/"+std::string(URL_CAPACITY,'x');
 assert(transport.start("https://github.com/owner/project/file",1024));worker();assert(opens==3&&cleanups==3);
 assert(transport.read(message)&&message.kind==FAILED);assert(strstr(reinterpret_cast<char*>(message.bytes),"address length"));
 redirectURL="https://untrusted.example/file";
 assert(transport.start("https://github.com/owner/project/file",1024));worker();assert(opens==4&&cleanups==4);assert(transport.read(message)&&message.kind==FAILED);
 rejectTLS=true;assert(transport.start("https://github.com/owner/project/file",1024));worker();assert(transport.read(message)&&message.kind==FAILED);
 assert(transport.lastResult()==-2&&transport.lastTransportError()==0x801a&&transport.lastTlsCode()==-9984&&transport.lastTlsFlags()==8&&transport.errorFreeHeap()==100000);
 assert(!transport.start("http://github.com/file",1024));
 for(auto* q:queues)delete q;
 puts("PASS: real transport handles long signed redirects, rejects oversized/untrusted redirects and captures TLS diagnostics; HTTP/TLS adapter simulated.");
}
