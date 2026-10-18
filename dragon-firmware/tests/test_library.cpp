#include "../DragonPrototype/DragonLibrary.h"
#include <cassert>
#include <cstdio>
using namespace DragonLibrary;
int main(){
 Library lib;assert(lib.begin());assert(lib.data.active==0);assert(lib.next(PRESET_COUNT-1)==0);
 auto data=lib.data;data.profiles[1].used=1;strcpy(data.profiles[1].name,"Child");data.active=1;
 auto& c=data.customs[0];c.used=1;c.owner=1;c.base=0;strcpy(c.name,"Spark");c.colorMask=1u<<FACE;c.colors[FACE]={1,2,3};c.effectZones[3]=1u<<LW;
 data.profiles[1].count=2;data.profiles[1].favorites[0]=PRESET_COUNT;data.profiles[1].favorites[1]=2;
 assert(lib.save(data));assert(lib.next(2)==PRESET_COUNT);assert(lib.next(PRESET_COUNT)==2);
 auto custom=lib.resolve(PRESET_COUNT);
 for(uint8_t i=0;i<64;i++){auto original=DRAGON_PRESETS[0].pixels[i];auto actual=custom.pixels[i];if(ZONES[i/8][i%8]==FACE){assert(actual.r==1&&actual.g==2&&actual.b==3);}else assert(!memcmp(&actual,&original,sizeof(RGB)));}
 assert(custom.effects==PRESET_GLITTER);assert(custom.animatedZones==(1u<<LW));
 assert(available(lib.data,PRESET_COUNT,0));assert(available(lib.data,PRESET_COUNT,2));assert(!contains(lib.data,PRESET_COUNT,2));assert(available(lib.data,PRESET_COUNT,1));
 Library reboot;assert(reboot.begin());assert(reboot.data.active==1);assert(!strcmp(reboot.data.customs[0].name,"Spark"));
 auto newer=lib.data;strcpy(newer.customs[0].name,"New name");assert(lib.save(newer));
 // Corrupt the newest snapshot; recovery selects the previous complete one.
 otherPreferences["dragon-library/a"][10]^=0x80;
 Library recovery;assert(recovery.begin());assert(!strcmp(recovery.data.customs[0].name,"Spark"));
 auto invalid=recovery.data;invalid.profiles[1].favorites[1]=PRESET_COUNT;assert(!recovery.save(invalid));
 invalid=recovery.data;invalid.customs[0].base=PRESET_COUNT;assert(!recovery.save(invalid));
 invalid=recovery.data;invalid.profiles[1].brightness=37;assert(!recovery.save(invalid));
 auto retained=recovery.data;failStore=true;auto failed=retained;strcpy(failed.profiles[1].name,"Unsaved");assert(!recovery.save(failed));assert(!memcmp(&retained,&recovery.data,sizeof(Data)));failStore=false;
 auto removed=recovery.data;assert(!eraseCustom(removed,0,1));assert(!eraseCustom(removed,PRESET_COUNT,0));assert(eraseCustom(removed,PRESET_COUNT,1));assert(removed.profiles[1].count==1&&removed.profiles[1].favorites[0]==2);assert(recovery.save(removed));assert(!available(recovery.data,PRESET_COUNT,1));
 auto profiles=recovery.data;profiles.profiles[2].used=1;strcpy(profiles.profiles[2].name,"Second");profiles.customs[1]=Custom{};profiles.customs[1].used=1;profiles.customs[1].owner=2;profiles.customs[1].base=0;strcpy(profiles.customs[1].name,"Keep me");profiles.active=2;
 assert(!contains(profiles,0,2));assert(contains(profiles,PRESET_COUNT+1,2));assert(contains(profiles,PRESET_COUNT+1,0));assert(!eraseProfile(profiles,0));assert(eraseProfile(profiles,2));assert(profiles.active==0&&!profiles.profiles[2].used&&profiles.customs[1].owner==0);assert(recovery.save(profiles));Library deleted;assert(deleted.begin());assert(!deleted.data.profiles[2].used);assert(!strcmp(deleted.data.profiles[0].name,"All"));assert(deleted.next(255)==DEFAULT_PRESET);
 auto tampered=deleted.data;strcpy(tampered.profiles[0].name,"Changed");tampered.profiles[0].count=1;tampered.profiles[0].favorites[0]=1;assert(deleted.save(tampered));assert(!strcmp(deleted.data.profiles[0].name,"All")&&deleted.data.profiles[0].count==0);
 // Old snapshots containing retired IDs remain valid; loading filters favourites
 // without shifting IDs or losing custom dragons based on the retired palettes.
 auto legacy=deleted.data;legacy.generation=100;legacy.profiles[1].used=1;
 strcpy(legacy.profiles[1].name,"Legacy");legacy.active=1;
 legacy.profiles[1].count=3;legacy.profiles[1].favorites[0]=8;
 legacy.profiles[1].favorites[1]=67;legacy.profiles[1].favorites[2]=1;
 legacy.customs[0].used=1;legacy.customs[0].owner=1;legacy.customs[0].base=8;
 strcpy(legacy.customs[0].name,"Keep legacy custom");legacy.checksum=checksum(legacy);
 assert(valid(legacy));Preferences oldStorage;assert(oldStorage.begin("dragon-library",false));
 assert(oldStorage.putBytes("a",&legacy,sizeof(legacy))==sizeof(legacy));
 Library upgraded;assert(upgraded.begin());assert(upgraded.data.active==1);
 assert(upgraded.data.profiles[1].count==1&&upgraded.data.profiles[1].favorites[0]==1);
 assert(upgraded.data.customs[0].base==8);assert(!strcmp(upgraded.resolve(PRESET_COUNT).name,"Keep legacy custom"));
 assert(!contains(upgraded.data,8,0)&&!contains(upgraded.data,67,1));
 assert(upgraded.save(upgraded.data));Library again;assert(again.begin());
 assert(again.data.customs[0].base==8&&again.data.profiles[1].count==1);
 puts("PASS: ownership, regions, persistence/corruption, failed saves, protected All and retired-ID compatibility.");
}
