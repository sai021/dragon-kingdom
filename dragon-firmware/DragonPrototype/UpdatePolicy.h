#pragma once
#include <stdint.h>
#include <stddef.h>
namespace DragonUpdate {
constexpr uint32_t MAX_IMAGE=0x180000,IDLE_MS=30000;
inline int nibble(char c){return c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:-1;}
inline bool decode(const char* text,size_t length,uint8_t* out,size_t size){
 if(length!=size*2)return false;for(size_t i=0;i<size;i++){int a=nibble(text[i*2]),b=nibble(text[i*2+1]);if(a<0||b<0)return false;out[i]=a*16+b;}return true;
}
struct Transfer {
 uint32_t size=0,offset=0,last=0;bool active=false;
 bool start(uint32_t total,uint32_t now){if(active||!total||total>MAX_IMAGE)return false;size=total;offset=0;last=now;active=true;return true;}
 bool accepts(uint32_t at,size_t count)const{return active&&at==offset&&count&&count<=512&&count<=size-offset;}
 bool complete()const{return active&&offset==size;}
 bool expired(uint32_t now)const{return active&&uint32_t(now-last)>=IDLE_MS;}
};
}
