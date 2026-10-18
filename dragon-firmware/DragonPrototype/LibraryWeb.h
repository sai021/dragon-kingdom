#pragma once
// Included inside DragonWeb, after the authenticated request helpers.
bool numberArgument(const char* key,int low,int high,int& result){String value=server.arg(key);if(value.length()>10)return false;char text[12];value.toCharArray(text,sizeof(text));return readNumber(text,low,high,result);}
bool nameArgument(char* output){String name=server.arg("name");name.trim();if(!name.length()||name.length()>32)return false;for(size_t i=0;i<name.length();i++)if(uint8_t(name[i])<32)return false;name.toCharArray(output,33);return true;}
String idList(const uint8_t* ids,uint8_t count){String out="[";for(uint8_t i=0;i<count;i++){if(i)out+=',';out+=String(ids[i]);}return out+"]";}
String colorHex(RGB color){char text[8];snprintf(text,sizeof(text),"#%02x%02x%02x",color.r,color.g,color.b);return text;}
bool parseList(const String& text,uint16_t* output,uint8_t maximum,uint8_t& count,uint16_t high){
 count=0;if(!text.length())return true;int start=0;
 while(start<int(text.length())){if(count>=maximum)return false;int end=text.indexOf(',',start);if(end<0)end=text.length();String part=text.substring(start,end);if(!part.length()||part.length()>5)return false;char buffer[8];part.toCharArray(buffer,sizeof(buffer));int value;if(!readNumber(buffer,0,high,value))return false;output[count++]=value;if(end==int(text.length()))return true;start=end+1;if(start==int(text.length()))return false;}
 return true;
}
// Bind writes to the collection the form actually loaded, including after a
// lost response or another tab changing the active profile. Storage is unchanged.
bool libraryContext(){
 int profile;String value=server.arg("generation");uint32_t generation=0;
 bool valid=numberArgument("profile",0,DragonLibrary::PROFILE_LIMIT-1,profile)&&value.length()>0&&value.length()<=10;
 for(size_t i=0;valid&&i<value.length();i++){
  char c=value[i];if(c<'0'||c>'9'||generation>(UINT32_MAX-uint32_t(c-'0'))/10u)valid=false;
  else generation=generation*10u+uint32_t(c-'0');
 }
 if(!valid||profile!=library.data.active||generation!=library.data.generation){
  server.send(409,"text/plain","Your collection changed. Reload the page before saving. Your changes have not been saved.");return false;
 }
 return true;
}
void registerLibraryRoutes(){
 server.on("/api/delete-profile",HTTP_POST,[]{
  if(!authorize()||!libraryContext())return;int id;auto candidate=library.data;
  if(!numberArgument("id",1,DragonLibrary::PROFILE_LIMIT-1,id)||!DragonLibrary::eraseProfile(candidate,id)){server.send(403,"text/plain","All is protected. Choose another existing profile.");return;}
  if(!library.save(candidate)){server.send(500,"text/plain","Profile could not be deleted. Your profiles were kept.");return;}
  const auto& p=library.data.profiles[library.data.active];setPalette(library.next(255));mode=DragonLibrary::contains(library.data,palette,library.data.active)?ZONE_VIEW:OFF;setBrightness(p.brightness);rememberLighting();reply(200,"{}");
 });
 server.on("/api/delete-custom",HTTP_POST,[]{
  if(!authorize()||!libraryContext())return;int id;auto candidate=library.data;
  if(!numberArgument("id",PRESET_COUNT,PRESET_COUNT+DragonLibrary::CUSTOM_LIMIT-1,id)||!DragonLibrary::eraseCustom(candidate,id,candidate.active)){server.send(403,"text/plain","Only your own custom dragons can be deleted.");return;}
  if(!library.save(candidate)){server.send(500,"text/plain","Dragon could not be deleted. Try again.");return;}
  if(palette==id){setPalette(library.next(255));mode=DragonLibrary::contains(library.data,palette,library.data.active)?ZONE_VIEW:OFF;rememberLighting();}reply(200,"{}");
 });
 server.on("/api/library",HTTP_GET,[]{
  if(!authorize())return;String out="{\"active\":"+String(library.data.active)+",\"generation\":"+String(library.data.generation)+",\"profiles\":[";unsigned added=0;
  for(uint8_t i=0;i<DragonLibrary::PROFILE_LIMIT;i++){const auto& p=library.data.profiles[i];if(!p.used)continue;if(added++)out+=',';out+="{\"id\":"+String(i)+",\"name\":"+quote(p.name)+",\"brightness\":"+String(p.brightness)+",\"favorites\":"+idList(p.favorites,p.count)+"}";}
  reply(200,out+"],\"customLimit\":"+String(DragonLibrary::CUSTOM_LIMIT)+"}");
 });
 server.on("/api/profile",HTTP_POST,[]{
  if(!authorize()||!libraryContext())return;auto candidate=library.data;String action=server.arg("action");int id=candidate.active;
  if(action=="select"){
   if(!numberArgument("id",0,DragonLibrary::PROFILE_LIMIT-1,id)||!candidate.profiles[id].used){server.send(400,"text/plain","Choose an existing profile.");return;}candidate.active=id;
  }else if(action=="create"||action=="update"){
   if(action=="create"){id=-1;for(uint8_t i=0;i<DragonLibrary::PROFILE_LIMIT;i++)if(!candidate.profiles[i].used){id=i;break;}if(id<0){server.send(409,"text/plain","All four profile spaces are in use.");return;}candidate.profiles[id]=DragonLibrary::Profile{};candidate.profiles[id].used=1;candidate.active=id;}
   auto& p=candidate.profiles[id];int glow;if((id!=0&&!nameArgument(p.name))||!numberArgument("brightness",10,100,glow)||glow%10){server.send(400,"text/plain","Use a name up to 32 bytes and a glow in steps of 10%.");return;}if(id!=0&&String(p.name).equalsIgnoreCase("All")){server.send(400,"text/plain","All is reserved for the complete collection. Choose another name.");return;}p.brightness=glow;
   uint16_t ids[DragonLibrary::FAVORITE_LIMIT];uint8_t count;
   if(!parseList(server.arg("favorites"),ids,DragonLibrary::FAVORITE_LIMIT,count,PRESET_COUNT+DragonLibrary::CUSTOM_LIMIT-1)){server.send(400,"text/plain","Choose up to twelve favourites.");return;}
   p.count=count;for(uint8_t i=0;i<count;i++){if(!DragonLibrary::selectable(candidate,ids[i],id)){server.send(400,"text/plain","That dragon is no longer available.");return;}for(uint8_t j=0;j<i;j++)if(ids[j]==ids[i]){server.send(400,"text/plain","A favourite was selected twice.");return;}p.favorites[i]=ids[i];}
  }else{server.send(400,"text/plain","Unknown profile action.");return;}
  if(!library.save(candidate)){server.send(500,"text/plain","Profile could not be saved. Your current profile was kept.");return;}
  const auto& p=library.data.profiles[library.data.active];setPalette(library.next(255));mode=DragonLibrary::contains(library.data,palette,library.data.active)?ZONE_VIEW:OFF;setBrightness(p.brightness);rememberLighting();reply(200,"{}");
 });
 server.on("/api/dragon-detail",HTTP_GET,[]{
  if(!authorize())return;int id;if(!numberArgument("id",0,PRESET_COUNT+DragonLibrary::CUSTOM_LIMIT-1,id)||!DragonLibrary::available(library.data,id,library.data.active)){server.send(404,"text/plain","Dragon not found in this profile.");return;}
  const auto p=library.resolve(id);bool custom=id>=PRESET_COUNT;uint8_t base=custom?library.data.customs[id-PRESET_COUNT].base:id;
  String out="{\"profile\":"+String(library.data.active)+",\"generation\":"+String(library.data.generation)+",\"id\":"+String(id)+",\"base\":"+String(base)+",\"name\":"+quote(p.name)+",\"colorMask\":"+String(custom?library.data.customs[id-PRESET_COUNT].colorMask:0)+",\"canEdit\":"+(custom&&library.data.customs[id-PRESET_COUNT].owner==library.data.active?"true":"false")+",\"colors\":[";
  for(uint8_t z=0;z<ZONE_COUNT;z++){if(z)out+=',';out+=quote(colorHex(p.zones[z]));}out+="],\"pixels\":[";
  for(uint8_t i=0;i<64;i++){if(i)out+=',';out+=quote(colorHex(p.pixels[i]));}out+="],\"zones\":[";
  for(uint8_t i=0;i<64;i++){if(i)out+=',';out+=String(unsigned(ZONES[i/8][i%8]));}out+="],\"effectZones\":[";
  for(uint8_t e=0;e<4;e++){if(e)out+=',';out+=String((p.effects&(1u<<e))?(p.effectZones[e]&p.animatedZones):0);}reply(200,out+"]}");
 });
 server.on("/api/custom",HTTP_POST,[]{
  if(!authorize()||!libraryContext())return;int id,base,mask;
  if(!numberArgument("id",-1,PRESET_COUNT+DragonLibrary::CUSTOM_LIMIT-1,id)||!numberArgument("base",0,PRESET_COUNT-1,base)||!numberArgument("colorMask",0,(1<<ZONE_COUNT)-1,mask)){server.send(400,"text/plain","Invalid dragon settings.");return;}
  auto candidate=library.data;int slot=id<0?-1:id-PRESET_COUNT;
  if(id<0){for(uint8_t i=0;i<DragonLibrary::CUSTOM_LIMIT;i++)if(!candidate.customs[i].used){slot=i;break;}}
  else if(slot<0||!candidate.customs[slot].used||candidate.customs[slot].owner!=candidate.active){server.send(403,"text/plain","Save a copy of this dragon instead.");return;}
  if(slot<0){server.send(409,"text/plain","All eight custom dragon spaces are full. You can edit an existing creation.");return;}
  DragonLibrary::Custom custom{};custom.used=1;custom.owner=candidate.active;custom.base=base;custom.colorMask=mask;
  if(!nameArgument(custom.name)){server.send(400,"text/plain","Give your dragon a name up to 32 bytes.");return;}
  String colors=server.arg("colors");if(colors.length()!=ZONE_COUNT*6){server.send(400,"text/plain","Invalid region colours.");return;}
  for(uint8_t z=0;z<ZONE_COUNT;z++){String part=colors.substring(z*6,z*6+6);for(uint8_t i=0;i<6;i++)if(!isxdigit(part[i])){server.send(400,"text/plain","Invalid colour.");return;}uint32_t rgb=strtoul(part.c_str(),nullptr,16);custom.colors[z]={uint8_t(rgb>>16),uint8_t(rgb>>8),uint8_t(rgb)};}
  uint8_t count;if(!parseList(server.arg("effectZones"),custom.effectZones,4,count,(1<<ZONE_COUNT)-1)||count!=4){server.send(400,"text/plain","Invalid region effects.");return;}
  candidate.customs[slot]=custom;if(!library.save(candidate)){server.send(500,"text/plain","Dragon could not be saved. Your previous creations were kept.");return;}
  setPalette(PRESET_COUNT+slot);mode=ZONE_VIEW;if(!brightness)setBrightness(100);rememberLighting();reply(200,"{\"id\":"+String(PRESET_COUNT+slot)+"}");
 });
}
