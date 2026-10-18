#pragma once
#include <stddef.h>
#include <stdint.h>
#include <string.h>

namespace DragonHttp {
constexpr size_t MAX_HEADERS=2048,MAX_BODY=1536,MAX_REQUEST=MAX_HEADERS+MAX_BODY;
constexpr uint32_t REQUEST_MS=3000,RESPONSE_MS=5000;
constexpr size_t WRITE_CHUNK=1024,MAX_RESPONSE=65536;
enum Result { WAIT, READY, REJECT };
inline bool equal(const char* text,size_t size,const char* expected){
 if(size!=strlen(expected))return false;
 for(size_t i=0;i<size;i++){char c=text[i];if(c>='A'&&c<='Z')c+=32;if(c!=expected[i])return false;}
 return true;
}
// Inspect the accumulated bytes. The pinned WebServer parser is only called
// once every byte it will read is present, with one supported request.
inline Result inspect(const char* bytes,size_t size){
 if(size>MAX_REQUEST||memchr(bytes,0,size))return REJECT;
 size_t end=0;
 for(size_t i=3;i<size;i++)if(!memcmp(bytes+i-3,"\r\n\r\n",4)){end=i+1;break;}
 if(!end)return size>=MAX_HEADERS?REJECT:WAIT;
 if(end>MAX_HEADERS)return REJECT;
 size_t line=0;while(line+1<end&&memcmp(bytes+line,"\r\n",2))line++;
 bool post=line>=5&&!memcmp(bytes,"POST ",5),get=line>=4&&!memcmp(bytes,"GET ",4);
 if((!post&&!get)||line>512)return REJECT;
 size_t path=post?5:4;
 if(bytes[path]!='/'||line<path+10)return REJECT;
 if(memcmp(bytes+line-9," HTTP/1.1",9)&&memcmp(bytes+line-9," HTTP/1.0",9))return REJECT;
 for(size_t i=path;i<line-9;i++)if(uint8_t(bytes[i])<=32||uint8_t(bytes[i])>=127)return REJECT;
 size_t content=0;bool lengthSeen=false,form=false;
 for(size_t start=line+2;start<end-2;){
  size_t stop=start;while(stop+1<end&&memcmp(bytes+stop,"\r\n",2))stop++;
  size_t colon=start;while(colon<stop&&bytes[colon]!=':')colon++;
  if(colon==start||colon==stop)return REJECT;
  for(size_t i=start;i<stop;i++)if((uint8_t(bytes[i])<32&&bytes[i]!='\t')||uint8_t(bytes[i])>=127)return REJECT;
  size_t value=colon+1;while(value<stop&&(bytes[value]==' '||bytes[value]=='\t'))value++;
  size_t valueEnd=stop;while(valueEnd>value&&(bytes[valueEnd-1]==' '||bytes[valueEnd-1]=='\t'))valueEnd--;
  if(equal(bytes+start,colon-start,"transfer-encoding")||equal(bytes+start,colon-start,"expect"))return REJECT;
  if(equal(bytes+start,colon-start,"content-length")){
   if(lengthSeen||value==valueEnd)return REJECT;lengthSeen=true;
   for(size_t i=value;i<valueEnd;i++){
    if(bytes[i]<'0'||bytes[i]>'9')return REJECT;
    content=content*10+size_t(bytes[i]-'0');if(content>MAX_BODY)return REJECT;
   }
  }
  if(equal(bytes+start,colon-start,"content-type")){
   const char* type="application/x-www-form-urlencoded";size_t length=strlen(type);
   form=valueEnd-value>=length&&equal(bytes+value,length,type)&&
    (valueEnd-value==length||bytes[value+length]==';');
  }
  start=stop+2;
 }
 if((get&&content)||(post&&(!lengthSeen||(content&&!form))))return REJECT;
 if(size>end+content)return REJECT; // No pipelining or unframed trailing bytes.
 return size==end+content?READY:WAIT;
}
}
