#include "../DragonPrototype/NetworkSerial.h"
#include <cassert>
#include <cstring>
#include <cstdio>
int main(){
 char value[65];using namespace DragonNetworkSerial;
 assert(decode("46616d696c792057692d4669",value,sizeof(value))&&!strcmp(value,"Family Wi-Fi"));
 assert(decode("",value,sizeof(value))&&!value[0]);
 assert(!decode("00",value,sizeof(value)));assert(!decode("a",value,sizeof(value)));assert(!decode("gg",value,sizeof(value)));
 char shortValue[2];assert(!decode("6162",shortValue,sizeof(shortValue)));assert(decode("61",shortValue,sizeof(shortValue)));
 assert(validPassword(""));assert(!validPassword("short"));assert(validPassword("sample123"));
 memset(value,'f',64);value[64]=0;assert(validPassword(value));value[63]='x';assert(!validPassword(value));
 puts("PASS: USB network credential framing, spaces, bounds, NUL rejection and Wi-Fi key validation.");
}
