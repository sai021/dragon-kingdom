#pragma once
#include "DragonPresets.h"
#include <Preferences.h>
#include <cstring>
#include <stddef.h>

namespace DragonLibrary {
using namespace Dragon;
constexpr uint8_t PROFILE_LIMIT=4,CUSTOM_LIMIT=8,FAVORITE_LIMIT=12;
static_assert(PRESET_COUNT==81,"Version-1 library IDs require the original 81 preset slots; migrate saved data before changing the catalog.");
static_assert(PRESET_COUNT+CUSTOM_LIMIT<=256,"Library IDs must fit in a byte");
struct Profile {uint8_t used=0;char name[33]{};uint8_t brightness=100,count=0,favorites[FAVORITE_LIMIT]{};};
struct Custom {uint8_t used=0,owner=0,base=0;char name[33]{};uint16_t colorMask=0;RGB colors[ZONE_COUNT]{};uint16_t effectZones[4]{};};
struct Data {uint32_t magic=0x444c4231,version=1,generation=0;uint8_t active=0;Profile profiles[PROFILE_LIMIT]{};Custom customs[CUSTOM_LIMIT]{};uint32_t checksum=0;};
inline uint32_t checksum(const Data& d){uint32_t hash=2166136261u;const auto* bytes=reinterpret_cast<const uint8_t*>(&d);for(size_t i=0;i<offsetof(Data,checksum);i++){hash^=bytes[i];hash*=16777619u;}return hash;}
inline bool available(const Data& d,uint8_t id,uint8_t owner){(void)owner;return id<PRESET_COUNT||(id<PRESET_COUNT+CUSTOM_LIMIT&&d.customs[id-PRESET_COUNT].used);}
inline bool selectable(const Data& d,uint8_t id,uint8_t owner){return available(d,id,owner)&&!(id<PRESET_COUNT&&PRESET_RETIRED[id]);}
inline void removeRetiredFavorites(Data& d){
 for(auto& p:d.profiles){if(p.count>FAVORITE_LIMIT)continue;uint8_t count=0;for(uint8_t i=0;i<p.count;i++)if(!(p.favorites[i]<PRESET_COUNT&&PRESET_RETIRED[p.favorites[i]]))p.favorites[count++]=p.favorites[i];p.count=count;}
}
inline bool contains(const Data& d,uint8_t id,uint8_t profile){
 if(!selectable(d,id,profile))return false;
 if(profile==0||(id>=PRESET_COUNT&&d.customs[id-PRESET_COUNT].owner==profile))return true;
 const auto& p=d.profiles[profile];for(uint8_t i=0;i<p.count;i++)if(p.favorites[i]==id)return true;return false;
}
inline bool eraseProfile(Data& d,uint8_t id){
 if(id==0||id>=PROFILE_LIMIT||!d.profiles[id].used)return false;
 for(auto& c:d.customs)if(c.used&&c.owner==id)c.owner=0;
 d.profiles[id]=Profile{};if(d.active==id)d.active=0;return true;
}
inline bool eraseCustom(Data& d,uint8_t id,uint8_t owner){
 if(id<PRESET_COUNT||!available(d,id,owner)||d.customs[id-PRESET_COUNT].owner!=owner)return false;
 d.customs[id-PRESET_COUNT]=Custom{};
 for(auto& p:d.profiles){uint8_t count=0;for(uint8_t i=0;i<p.count;i++)if(p.favorites[i]!=id)p.favorites[count++]=p.favorites[i];p.count=count;}
 return true;
}
inline bool valid(const Data& d){
 if(d.magic!=0x444c4231||d.version!=1||d.active>=PROFILE_LIMIT||!d.profiles[d.active].used||d.checksum!=checksum(d))return false;
 for(auto& p:d.profiles)if(p.used){if(!p.name[0]||!memchr(p.name,0,sizeof(p.name))||p.count>FAVORITE_LIMIT||p.brightness<10||p.brightness>100||p.brightness%10)return false;}
 for(auto& c:d.customs)if(c.used){if(c.owner>=PROFILE_LIMIT||!d.profiles[c.owner].used||c.base>=PRESET_COUNT||!c.name[0]||!memchr(c.name,0,sizeof(c.name))||(c.colorMask>>ZONE_COUNT))return false;for(auto mask:c.effectZones)if(mask>>ZONE_COUNT)return false;}
 for(uint8_t i=0;i<PROFILE_LIMIT;i++)if(d.profiles[i].used)for(uint8_t j=0;j<d.profiles[i].count;j++){if(!available(d,d.profiles[i].favorites[j],i))return false;for(uint8_t k=0;k<j;k++)if(d.profiles[i].favorites[k]==d.profiles[i].favorites[j])return false;}
 return true;
}
class Library {
 Preferences storage;bool ready=false;uint8_t slot=0;
 public:
 Data data{};
 bool isReady()const{return ready;}
 void defaults(){data=Data{};data.profiles[0].used=1;strcpy(data.profiles[0].name,"All");}
 Library(){defaults();}
 bool begin(){
  ready=storage.begin("dragon-library",false);if(!ready)return false;
  Data a{},b{};bool va=storage.getBytesLength("a")==sizeof(a)&&storage.getBytes("a",&a,sizeof(a))==sizeof(a)&&valid(a);
  bool vb=storage.getBytesLength("b")==sizeof(b)&&storage.getBytes("b",&b,sizeof(b))==sizeof(b)&&valid(b);
  if(vb&&(!va||int32_t(b.generation-a.generation)>0)){data=b;slot=1;}else if(va){data=a;slot=0;}else defaults();
  removeRetiredFavorites(data);data.profiles[0].used=1;strcpy(data.profiles[0].name,"All");data.profiles[0].count=0;data.checksum=checksum(data);return true;
 }
 bool save(Data candidate){
  if(!ready)return false;removeRetiredFavorites(candidate);candidate.profiles[0].used=1;strcpy(candidate.profiles[0].name,"All");candidate.profiles[0].count=0;candidate.generation=data.generation+1;candidate.checksum=checksum(candidate);if(!valid(candidate))return false;
  const char* key=slot?"a":"b";Data check{};
  if(storage.putBytes(key,&candidate,sizeof(candidate))!=sizeof(candidate)||storage.getBytes(key,&check,sizeof(check))!=sizeof(check)||!valid(check)||memcmp(&candidate,&check,sizeof(check)))return false;
  data=check;slot^=1;return true;
 }
 uint8_t next(uint8_t current)const{
  if(data.active){
   const auto& p=data.profiles[data.active];uint8_t ids[FAVORITE_LIMIT+CUSTOM_LIMIT],count=0;
   for(uint8_t i=0;i<p.count;i++)if(contains(data,p.favorites[i],data.active))ids[count++]=p.favorites[i];
   for(uint8_t slot=0;slot<CUSTOM_LIMIT;slot++){uint8_t id=PRESET_COUNT+slot;if(!contains(data,id,data.active))continue;bool duplicate=false;for(uint8_t i=0;i<count;i++)if(ids[i]==id)duplicate=true;if(!duplicate)ids[count++]=id;}
   if(!count)return DEFAULT_PRESET;for(uint8_t i=0;i<count;i++)if(ids[i]==current)return ids[(i+1)%count];return ids[0];
  }
  if(current>=PRESET_COUNT+CUSTOM_LIMIT)return DEFAULT_PRESET;
  for(uint16_t step=1;step<=PRESET_COUNT+CUSTOM_LIMIT;step++){uint8_t id=(current+step)%(PRESET_COUNT+CUSTOM_LIMIT);if(contains(data,id,0))return id;}return DEFAULT_PRESET;
 }
 DragonPreset resolve(uint8_t id)const{
  if(id<PRESET_COUNT)return DRAGON_PRESETS[id];
  if(!available(data,id,data.active))return DRAGON_PRESETS[DEFAULT_PRESET];
  const auto& c=data.customs[id-PRESET_COUNT];DragonPreset p=DRAGON_PRESETS[c.base];p.name=c.name;p.id="custom";p.effects=0;p.animatedZones=0;
  for(uint8_t e=0;e<4;e++){p.effectZones[e]=c.effectZones[e];if(p.effectZones[e])p.effects|=1u<<e;p.animatedZones|=p.effectZones[e];}
  for(uint8_t z=0;z<ZONE_COUNT;z++)if(c.colorMask&(1u<<z))p.zones[z]=c.colors[z];
  for(uint8_t i=0;i<64;i++)if(c.colorMask&(1u<<ZONES[i/8][i%8]))p.pixels[i]=c.colors[ZONES[i/8][i%8]];
  return p;
 }
};
}
