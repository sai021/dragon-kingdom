#pragma once
#include "OnlinePolicy.h"
#include <atomic>
#include <esp_http_client.h>
#include <esp_crt_bundle.h>
#include <freertos/FreeRTOS.h>
#include <freertos/task.h>
#include <freertos/queue.h>
namespace DragonOnline {
// Worker owns HTTPS only. The lighting loop owns OTA, sessions and all web state.
// A bounded queue prevents the downloader from outrunning main-loop flash writes.
class Transport {
 QueueHandle_t queue=nullptr;
 std::atomic<bool> working{false},cancelled{false};
 char target[1024]{};uint32_t maximum=0;
 struct Redirect {char url[1024]{};};
 static esp_err_t event(esp_http_client_event_t* event){
  if(event->event_id==HTTP_EVENT_ON_HEADER&&event->header_key&&event->header_value&&!strcasecmp(event->header_key,"Location")){
   auto* redirect=(Redirect*)event->user_data;snprintf(redirect->url,sizeof(redirect->url),"%s",event->header_value);
  }return ESP_OK;
 }
 bool send(Message& message){while(!cancelled.load()){if(xQueueSend(queue,&message,pdMS_TO_TICKS(100))==pdTRUE)return true;}return false;}
 void failure(const char* text){Message m;m.kind=FAILED;m.size=strlen(text);memcpy(m.bytes,text,m.size);send(m);}
 static void task(void* pointer){auto* self=(Transport*)pointer;self->download();self->working.store(false);vTaskDelete(nullptr);}
 void download(){
  char url[1024];strcpy(url,target);uint32_t since=millis();
  for(unsigned redirects=0;redirects<=4&&!cancelled.load();redirects++){
   if(!allowedURL(url)){failure("Update redirect was not a trusted HTTPS release host.");return;}
   Redirect redirect;esp_http_client_config_t config{};config.url=url;config.timeout_ms=5000;config.disable_auto_redirect=true;config.crt_bundle_attach=esp_crt_bundle_attach;config.transport_type=HTTP_TRANSPORT_OVER_SSL;config.buffer_size=1024;config.buffer_size_tx=512;config.event_handler=event;config.user_data=&redirect;
   auto client=esp_http_client_init(&config);if(!client){failure("Not enough memory for HTTPS. Try again or upload a file.");return;}
   esp_http_client_set_header(client,"User-Agent","Dragon-Kingdom/0.3");
   if(esp_http_client_open(client,0)!=ESP_OK){esp_http_client_cleanup(client);failure("Could not establish verified HTTPS. Check internet and the clock.");return;}
   int64_t length=esp_http_client_fetch_headers(client);int status=esp_http_client_get_status_code(client);
   if(status==301||status==302||status==303||status==307||status==308){esp_http_client_cleanup(client);if(!redirect.url[0])break;strcpy(url,redirect.url);continue;}
   if(status!=200||length>maximum){esp_http_client_cleanup(client);failure(status==404?"No signed online release is published yet. File upload is still available.":"Release download failed or exceeded the expected size.");return;}
   uint32_t received=0;bool ok=true;
   while(!cancelled.load()){
    if(uint32_t(millis()-since)>180000){ok=false;break;}
    Message m;int count=esp_http_client_read(client,(char*)m.bytes,sizeof(m.bytes));
    if(count<0){ok=false;break;}if(!count){ok=esp_http_client_is_complete_data_received(client);break;}
    if(uint32_t(count)>maximum-received){ok=false;break;}received+=count;m.size=count;if(!send(m)){ok=false;break;}
   }
   esp_http_client_cleanup(client);
   if(cancelled.load())return;
   if(!ok||!received){failure("Download interrupted. Existing firmware was kept. Try again.");return;}
   Message done;done.kind=DONE;send(done);return;
  }
  if(!cancelled.load())failure("Too many HTTPS redirects. Existing firmware was kept.");
 }
 public:
 bool running()const{return working.load();}
 void cancel(){cancelled.store(true);}
 bool start(const char* url,uint32_t limit){
  if(running()||!allowedURL(url)||strlen(url)>=sizeof(target))return false;
  if(!queue)queue=xQueueCreate(4,sizeof(Message));if(!queue)return false;xQueueReset(queue);
  strcpy(target,url);maximum=limit;cancelled.store(false);working.store(true);
  if(xTaskCreate(task,"dragon-download",8192,this,1,nullptr)!=pdPASS){working.store(false);return false;}return true;
 }
 bool read(Message& message){return queue&&xQueueReceive(queue,&message,0)==pdTRUE;}
};
}
