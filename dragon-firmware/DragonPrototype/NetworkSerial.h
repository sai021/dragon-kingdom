#pragma once
#include <stddef.h>
namespace DragonNetworkSerial {
inline int hexDigit(char c){return c>='0'&&c<='9'?c-'0':c>='a'&&c<='f'?c-'a'+10:c>='A'&&c<='F'?c-'A'+10:-1;}
// Hex framing accepts spaces/UTF-8 without echoing a credential in responses.
inline bool decode(const char* input,char* output,size_t capacity){
 size_t size=0;
 while(*input){
  int a=hexDigit(*input++);if(!*input)return false;int b=hexDigit(*input++);
  if(a<0||b<0||size+1>=capacity||!(a||b))return false;
  output[size++]=char((a<<4)|b);
 }
 output[size]=0;return true;
}
inline bool validPassword(const char* key){
 size_t size=0;while(key[size])size++;
 if(size==0||(size>=8&&size<=63))return true;
 if(size!=64)return false;
 for(size_t i=0;i<size;i++)if(hexDigit(key[i])<0)return false;
 return true;
}
}
