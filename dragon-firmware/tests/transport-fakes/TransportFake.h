#pragma once
#include <cstdint>
#include <cstring>
#include <strings.h>
#include <cstdio>
#include <string>
#include <vector>
#include <deque>
#include <functional>
using esp_err_t=int;
constexpr int ESP_OK=0,HTTP_EVENT_ON_HEADER=3,HTTP_TRANSPORT_OVER_SSL=1,pdTRUE=1,pdPASS=1;
inline uint32_t millis(){return 100;}
inline unsigned pdMS_TO_TICKS(unsigned n){return n;}
struct FakeESP {uint32_t getFreeHeap(){return 100000;}uint32_t getMaxAllocHeap(){return 80000;}};inline FakeESP ESP;
struct esp_http_client_event_t {int event_id;void* user_data;char* header_key;char* header_value;};
inline int esp_crt_bundle_attach(void*){return 0;}
struct esp_http_client_config_t {const char* url=nullptr;int timeout_ms=0;bool disable_auto_redirect=false;int (*crt_bundle_attach)(void*)=nullptr;int transport_type=0,buffer_size=0,buffer_size_tx=0;int (*event_handler)(esp_http_client_event_t*)=nullptr;void* user_data=nullptr;};
struct FakeHTTP {esp_http_client_config_t config;std::string url;unsigned read=0;};
using esp_http_client_handle_t=FakeHTTP*;
inline std::string redirectURL,payload="signed manifest fixture";
inline unsigned opens=0,cleanups=0;inline bool rejectTLS=false;
inline esp_http_client_handle_t esp_http_client_init(const esp_http_client_config_t* c){auto* p=new FakeHTTP;p->config=*c;p->url=c->url;return p;}
inline void esp_http_client_set_header(esp_http_client_handle_t,const char*,const char*){}
inline int esp_http_client_open(esp_http_client_handle_t c,int){
 opens++;if(rejectTLS)return -2;
 // Real IDF requires the request-target and protocol to fit before sending headers.
 const auto slash=c->url.find('/',8);const auto line=std::string("GET ")+c->url.substr(slash)+" HTTP/1.1\r\n";
 return line.size()>=size_t(c->config.buffer_size_tx)?-1:0;
}
inline int64_t esp_http_client_fetch_headers(esp_http_client_handle_t c){
 if(c->url.find("github.com/")!=std::string::npos){char key[]="Location";esp_http_client_event_t event{HTTP_EVENT_ON_HEADER,c->config.user_data,key,redirectURL.data()};c->config.event_handler(&event);return 0;}
 return payload.size();
}
inline int esp_http_client_get_status_code(esp_http_client_handle_t c){return c->url.find("github.com/")!=std::string::npos?302:200;}
inline int esp_http_client_read(esp_http_client_handle_t c,char* b,int count){if(c->read)return 0;unsigned n=payload.size()<size_t(count)?payload.size():count;memcpy(b,payload.data(),n);c->read+=n;return n;}
inline bool esp_http_client_is_complete_data_received(esp_http_client_handle_t c){return c->read==payload.size();}
inline void esp_http_client_cleanup(esp_http_client_handle_t c){cleanups++;delete c;}
inline int esp_http_client_get_and_clear_last_tls_error(esp_http_client_handle_t,int* code,int* flags){*code=rejectTLS?-9984:0;*flags=rejectTLS?8:0;return rejectTLS?0x801a:0;}
inline int esp_http_client_get_errno(esp_http_client_handle_t){return 0;}
struct FakeQueue {size_t size;std::deque<std::vector<uint8_t>> values;};
using QueueHandle_t=FakeQueue*;
inline std::vector<FakeQueue*> queues;
inline QueueHandle_t xQueueCreate(int,size_t size){auto* q=new FakeQueue{size,{}};queues.push_back(q);return q;}
inline void xQueueReset(QueueHandle_t q){q->values.clear();}
inline int xQueueSend(QueueHandle_t q,const void* data,int){auto* p=static_cast<const uint8_t*>(data);q->values.emplace_back(p,p+q->size);return pdTRUE;}
inline int xQueueReceive(QueueHandle_t q,void* data,int){if(q->values.empty())return 0;memcpy(data,q->values.front().data(),q->size);q->values.pop_front();return pdTRUE;}
inline std::function<void()> worker;
inline int xTaskCreate(void (*fn)(void*),const char*,int,void* ptr,int,void*){worker=[=]{fn(ptr);};return pdPASS;}
inline void vTaskDelete(void*){}
