#pragma once
#include <stdint.h>
#include <stddef.h>
#include <string.h>
namespace DragonParent {
constexpr const char* PASSWORD="dragon123";
constexpr uint32_t SESSION_MS=15*60*1000,COOLDOWN_MS=5000;
inline bool equal(const uint8_t* a,const uint8_t* b,size_t n){uint8_t diff=0;for(size_t i=0;i<n;i++)diff|=a[i]^b[i];return diff==0;}
inline bool live(uint32_t now,uint32_t issued,uint32_t duration){return uint32_t(now-issued)<duration;}
struct Session {
 char token[65]{};uint32_t issued=0;
 void clear(){memset(token,0,sizeof(token));}
 bool accepts(const char* value,uint32_t now)const{return token[0]&&strlen(value)==64&&live(now,issued,SESSION_MS)&&equal((const uint8_t*)token,(const uint8_t*)value,64);}
};
}
