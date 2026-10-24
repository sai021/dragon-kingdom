#pragma once
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "UpdatePolicy.h"
#include "CompatibilityPolicy.h"
namespace DragonOnline {
constexpr const char* CURRENT_TAG="v0.3.0-beta.4";
inline bool releaseTag(const char* tag){if(*tag!='v')return false;for(tag++;*tag;tag++)if((*tag<'0'||*tag>'9')&&*tag!='.')return false;return true;}
inline bool channelTag(const char* channel,const char* tag){return !strcmp(channel,"beta")?strstr(tag,"-beta.")!=nullptr:releaseTag(tag);}
constexpr size_t MANIFEST_MAX=1024;
struct Manifest {char board[3]{},tag[49]{},hash[65]{},signature[513]{};uint32_t size=0,capabilities=0,schema=0;};
inline bool validTag(const char* tag){size_t n=strlen(tag);if(!n||n>48)return false;for(size_t i=0;i<n;i++){char c=tag[i];if(!((c>='a'&&c<='z')||(c>='A'&&c<='Z')||(c>='0'&&c<='9')||c=='.'||c=='_'||c=='-'))return false;}return true;}
inline bool allowedURL(const char* url){
 const char* hosts[]={"https://github.com/","https://release-assets.githubusercontent.com/","https://objects.githubusercontent.com/"};
 for(auto host:hosts)if(!strncmp(url,host,strlen(host)))return true;return false;
}
inline bool parse(const char* data,size_t length,Manifest& out){
 if(!length||length>MANIFEST_MAX||memchr(data,0,length))return false;
 char text[MANIFEST_MAX+1];memcpy(text,data,length);text[length]=0;
 char* lines[8];char* cursor=text;
 for(unsigned i=0;i<8;i++){lines[i]=cursor;char* newline=strchr(cursor,'\n');if(!newline)return false;*newline=0;cursor=newline+1;}
 if(*cursor||strcmp(lines[0],"dragon-update-v2")||(strcmp(lines[1],"s3")&&strcmp(lines[1],"c3"))||!validTag(lines[2]))return false;
 uint32_t size=0;size_t digits=strlen(lines[3]);if(!digits||digits>7)return false;
 for(size_t i=0;i<digits;i++){char c=lines[3][i];if(c<'0'||c>'9')return false;size=size*10+c-'0';}
 if(!size||size>DragonUpdate::MAX_IMAGE||strlen(lines[4])!=64||strlen(lines[7])!=512)return false;
 for(size_t i=0;i<64;i++)if(DragonUpdate::nibble(lines[4][i])<0)return false;
 for(size_t i=0;i<512;i++)if(DragonUpdate::nibble(lines[7][i])<0)return false;
 uint32_t capabilities=0,schema=0;
 const char* cp=lines[5];const char* sp=lines[6];
 if(!DragonCompatibility::number(cp,capabilities)||*cp||!DragonCompatibility::number(sp,schema)||*sp)return false;
 out=Manifest{};out.capabilities=capabilities;out.schema=schema;strcpy(out.board,lines[1]);strcpy(out.tag,lines[2]);strcpy(out.hash,lines[4]);strcpy(out.signature,lines[7]);out.size=size;return true;
}
enum Kind:uint8_t {DATA,DONE,FAILED};
struct Message {Kind kind=DATA;uint16_t size=0;uint8_t bytes[512]{};};
}
