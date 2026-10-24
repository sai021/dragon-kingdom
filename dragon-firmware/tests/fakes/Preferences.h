#pragma once
#include <vector>
#include <cstring>
#include <map>
#include <string>
inline std::map<std::string,std::vector<unsigned char>> otherPreferences;
inline std::vector<unsigned char> persisted;
inline bool failStore=false;
inline unsigned storeWrites=0,failWriteAt=0,partialWriteAt=0;
struct Preferences {
 std::string space;
 bool begin(const char* name,bool){space=name;return true;}
 std::vector<unsigned char>& bytes(const char* key){return space=="dragon-power"?persisted:otherPreferences[space+"/"+key];}
 bool isKey(const char* key){return !bytes(key).empty();}
 bool remove(const char* key){bytes(key).clear();return true;}
 size_t getBytesLength(const char* key){return bytes(key).size();}
 size_t putBytes(const char* key,const void* data,size_t len){++storeWrites;if(failStore||(failWriteAt&&storeWrites==failWriteAt))return 0;auto p=static_cast<const unsigned char*>(data);if(partialWriteAt&&storeWrites==partialWriteAt){bytes(key).assign(p,p+len/2);return len/2;}bytes(key).assign(p,p+len);return len;}
 size_t getBytes(const char* key,void* data,size_t len){if(bytes(key).size()!=len)return 0;memcpy(data,bytes(key).data(),len);return len;}
};
