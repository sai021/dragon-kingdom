#pragma once
#include <stdint.h>
#include <string.h>
namespace DragonCompatibility {
// Schema 1 describes the complete existing library/alarm/rotation/backup contract.
constexpr uint32_t SCHEMA=1, CHIP_CALIBRATION=1;
struct Version {uint32_t part[4]{};bool stable=true;};
inline bool number(const char*& p,uint32_t& value){
 if(*p<'0'||*p>'9')return false;value=0;
 if(*p=='0'&&p[1]>='0'&&p[1]<='9')return false;
 while(*p>='0'&&*p<='9'){if(value>100000)return false;value=value*10+*p++-'0';}return true;
}
inline bool version(const char* p,Version& v){
 v={};if(*p++!='v')return false;
 for(unsigned i=0;i<3;i++){if(!number(p,v.part[i]))return false;if(i<2&&*p++!='.')return false;}
 if(!*p)return true;
 if(strncmp(p,"-beta.",6))return false;p+=6;v.stable=false;
 return number(p,v.part[3])&&!*p;
}
inline int compare(const Version& a,const Version& b){
 for(unsigned i=0;i<3;i++)if(a.part[i]!=b.part[i])return a.part[i]>b.part[i]?1:-1;
 if(a.stable!=b.stable)return a.stable?1:-1;
 return a.part[3]==b.part[3]?0:a.part[3]>b.part[3]?1:-1;
}
inline bool compatible(uint32_t capabilities,uint32_t schema,bool calibrated){
 return schema==SCHEMA&&(!calibrated||(capabilities&CHIP_CALIBRATION));
}
inline bool allowed(const char* target,const char* current,bool returnToRelease){
 Version a,b;if(!version(target,a)||!version(current,b))return false;
 return returnToRelease?a.stable:compare(a,b)>0;
}
}
