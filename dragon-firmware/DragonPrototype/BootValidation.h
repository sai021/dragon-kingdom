#pragma once
#include <stdint.h>
namespace DragonBoot {
enum class State {Valid,Trial,Migration,Unknown};
enum class Action {None,Confirm,SeedAndConfirm,Rollback};
struct Validation {
 State state=State::Unknown;bool attempted=false;const char* reason="awaiting startup";
 Action decide(uint32_t uptime,bool healthy){
  if(state==State::Valid){reason=healthy?"valid application":"valid application; degraded startup";return Action::None;}
  if(attempted)return Action::None;
  if(state==State::Unknown){reason="unrecognised OTA state; service required";return Action::None;}
  if(uptime>=30000&&healthy){attempted=true;reason="confirming startup";return state==State::Trial?Action::Confirm:Action::SeedAndConfirm;}
  if(uptime>=60000){
   reason=state==State::Trial?"trial startup failed":"migration degraded; service required";
   attempted=true;return state==State::Trial?Action::Rollback:Action::None;
  }return Action::None;
 }
};
}
