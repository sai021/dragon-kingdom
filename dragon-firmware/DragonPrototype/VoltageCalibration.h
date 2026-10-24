#pragma once
#include <stdint.h>
namespace DragonVoltage {
constexpr uint32_t MAGIC=0x56434131;
struct Record {uint64_t identity=0;uint32_t magic=MAGIC;uint16_t permille=1000,reserved=0;uint32_t checksum=0;};
inline uint32_t checksum(const Record& r){uint32_t h=2166136261u;for(unsigned n=0;n<8;n++){h^=uint8_t(r.identity>>(8*n));h*=16777619u;}for(unsigned n=0;n<2;n++){h^=uint8_t(r.permille>>(8*n));h*=16777619u;}return h^r.magic;}
inline Record make(uint64_t identity,uint16_t permille){Record r;r.identity=identity;r.permille=permille;r.checksum=checksum(r);return r;}
inline bool valid(const Record& r,uint64_t identity){return identity&&r.identity==identity&&r.magic==MAGIC&&!r.reserved&&r.permille>=500&&r.permille<=3000&&r.checksum==checksum(r);}
inline uint16_t correction(const Record& r,uint64_t identity){return valid(r,identity)?r.permille:1000;}
}
