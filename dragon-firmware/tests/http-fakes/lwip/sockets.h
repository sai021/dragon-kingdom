#pragma once
#include <errno.h>
constexpr int MSG_PEEK=1,MSG_DONTWAIT=2;
inline int recv(int socket,void* buffer,size_t size,int flags){
 assert(flags==MSG_DONTWAIT);auto& peer=*httpPeers[socket];
 if(peer.input.empty()){errno=EAGAIN;return -1;}
 size=std::min(size,std::min(peer.input.size(),peer.readLimit));memcpy(buffer,peer.input.data(),size);peer.input.erase(0,size);return int(size);
}
inline int send(int socket,const void* buffer,size_t size,int flags){
 assert(flags==MSG_DONTWAIT&&size<=1024);auto& peer=*httpPeers[socket];
 if(peer.blocked){errno=EWOULDBLOCK;return -1;}
 size=std::min(size,peer.writeLimit);peer.output.append(static_cast<const char*>(buffer),size);return int(size);
}
