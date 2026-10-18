#pragma once
#include "Arduino.h"
#include "WebString.h"
#include <memory>
#include <vector>
#include <cassert>
using PGM_P=const char*;
enum HTTPClientStatus { HC_NONE, HC_WAIT_READ };
struct HttpPeer {std::string input,output;bool connected=true,blocked=false;size_t writeLimit=1024,readLimit=1024;};
inline std::vector<std::shared_ptr<HttpPeer>> httpPeers;
inline unsigned httpHandled=0;
inline std::string httpParsed;
constexpr size_t CONTENT_LENGTH_NOT_SET=size_t(-2);
inline std::string httpResponse="HTTP/1.1 200 OK\r\nContent-Length: 2\r\n\r\n{}";
class NetworkClient {
 int socket=-1;
 public:
 NetworkClient()=default;
 virtual ~NetworkClient()=default;
 explicit NetworkClient(int id):socket(id){}
 int fd()const{return socket;}
 bool connected()const{return socket>=0&&httpPeers[socket]->connected;}
 explicit operator bool()const{return connected();}
 void stop(){if(socket>=0)httpPeers[socket]->connected=false;}
 void setTimeout(unsigned){}
 virtual int available(){return 0;}
 virtual int read(){return -1;}
 virtual int peek(){return -1;}
 virtual int read(uint8_t*,size_t){return 0;}
 virtual size_t readBytes(char*,size_t){return 0;}
};
struct NetworkServer {
 NetworkClient next;
 NetworkClient accept(){auto result=next;next=NetworkClient();return result;}
};
class WebServer {
 protected:
 NetworkServer _server;
 NetworkClient _currentClient;
 HTTPClientStatus _currentStatus=HC_NONE;
 size_t _contentLength=0;int _responseCode=0;
 std::unique_ptr<int> _currentUpload,_currentRaw;
 void _clearResponseHeaders(){}
 bool _parseRequest(NetworkClient& client){
  httpParsed.clear();while(client.available())httpParsed+=char(client.read());return true;
 }
 bool _handleRequest(){
  httpHandled++;
  _currentClientWrite(httpResponse.data(),10);
  _currentClientWrite_P(httpResponse.data()+10,httpResponse.size()-10);return true;
 }
 virtual size_t _currentClientWrite(const char*,size_t){assert(false);return 0;}
 virtual size_t _currentClientWrite_P(PGM_P,size_t){assert(false);return 0;}
 public:
 explicit WebServer(int){}
 virtual ~WebServer()=default;
 virtual void close(){}
 virtual void handleClient(){assert(false);}
 void acceptPeer(const std::shared_ptr<HttpPeer>& peer){httpPeers.push_back(peer);_server.next=NetworkClient(int(httpPeers.size()-1));}
};
