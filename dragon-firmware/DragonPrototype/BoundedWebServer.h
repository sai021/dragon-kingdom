#pragma once
#include <WebServer.h>
#include <lwip/sockets.h>
#include <errno.h>
#include "HttpRequestPolicy.h"

// Adapter for the pinned Arduino-ESP32 3.2.1 WebServer. Keep authentication,
// form decoding and routes there; bound transport work here on the main loop.
class BufferedRequestClient : public NetworkClient {
 const char* bytes;size_t size,position=0;
 public:
 BufferedRequestClient(const char* data,size_t length):bytes(data),size(length){setTimeout(0);}
 int available() override{return int(size-position);}
 int peek() override{return position<size?uint8_t(bytes[position]):-1;}
 int read() override{return position<size?uint8_t(bytes[position++]):-1;}
 int read(uint8_t* output,size_t length) override{
  if(length>size-position)length=size-position;
  memcpy(output,bytes+position,length);position+=length;return int(length);
 }
 size_t readBytes(char* output,size_t length) override{return size_t(read(reinterpret_cast<uint8_t*>(output),length));}
};

class BoundedWebServer : public WebServer {
 NetworkClient output;
 char input[DragonHttp::MAX_REQUEST+1];
 String response;
 size_t sent=0,received=0;
 uint32_t receivedAt=0,respondedAt=0;
 bool failed=false;
 void discardInput(){_currentClient.stop();_currentClient=NetworkClient();_currentStatus=HC_NONE;}
 void discardOutput(){output.stop();output=NetworkClient();response="";sent=0;}
 size_t append(const char* bytes,size_t size){
  if(failed||size>DragonHttp::MAX_RESPONSE-response.length()||!response.concat(bytes,size)){failed=true;return 0;}
  return size;
 }
 protected:
 size_t _currentClientWrite(const char* bytes,size_t size) override{return append(bytes,size);}
 size_t _currentClientWrite_P(PGM_P bytes,size_t size) override{return append(bytes,size);}
 public:
 explicit BoundedWebServer(int port):WebServer(port){}
 bool sending()const{return response.length()!=0;}
 void close() override{discardOutput();discardInput();WebServer::close();}
 void handleClient() override{
  uint32_t now=millis();
  if(sending()){
   if(!output.connected()||uint32_t(now-respondedAt)>=DragonHttp::RESPONSE_MS){discardOutput();return;}
   size_t count=response.length()-sent;if(count>DragonHttp::WRITE_CHUNK)count=DragonHttp::WRITE_CHUNK;
   int written=::send(output.fd(),response.c_str()+sent,count,MSG_DONTWAIT);
   if(written>0)sent+=size_t(written);
   else if(written==0||(errno!=EAGAIN&&errno!=EWOULDBLOCK)){discardOutput();return;}
   if(sent==response.length())discardOutput();
   return;
  }
  if(_currentStatus==HC_NONE){
   _currentClient=_server.accept();if(!_currentClient)return;
   _currentStatus=HC_WAIT_READ;receivedAt=now;received=0;
  }
  if(!_currentClient.connected()||uint32_t(now-receivedAt)>=DragonHttp::REQUEST_MS){discardInput();return;}
  // Consume incrementally: MSG_PEEK can expose just the first TCP segment on
  // lwIP. Buffering supports fragmented headers/bodies without waiting in read.
  size_t room=sizeof(input)-received;if(room>DragonHttp::WRITE_CHUNK)room=DragonHttp::WRITE_CHUNK;
  int count=::recv(_currentClient.fd(),input+received,room,MSG_DONTWAIT);
  if(count<0){if(errno!=EAGAIN&&errno!=EWOULDBLOCK)discardInput();return;}
  if(!count){discardInput();return;}
  received+=size_t(count);
  auto frame=DragonHttp::inspect(input,received);
  if(frame==DragonHttp::REJECT){discardInput();return;}
  if(frame==DragonHttp::WAIT)return;
  // Parse from memory so the dependency cannot wait for further socket input.
  // Supported routes use send/send_P (no uploads, raw handlers or middleware).
  output=_currentClient;response="";sent=0;failed=false;
  BufferedRequestClient request(input,received);
  if(_parseRequest(request)){
   _contentLength=CONTENT_LENGTH_NOT_SET;_responseCode=0;_clearResponseHeaders();_handleRequest();
  }
  _currentClient=NetworkClient();_currentStatus=HC_NONE;
  _currentUpload.reset();_currentRaw.reset();
  respondedAt=millis();
  if(failed||!sending())discardOutput();
 }
};
