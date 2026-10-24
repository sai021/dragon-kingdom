#pragma once
// Generated from web/dragon-kingdom.html by tools/embed_web.py.
const char page[] PROGMEM=R"DRAGONWEB(<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#19182d"><title>Dragon Kingdom</title>
<style>
*{box-sizing:border-box}[hidden]{display:none!important}body{font:18px system-ui,sans-serif;background:#19182d;color:#fff9ef;max-width:560px;margin:auto;padding:22px 18px 40px}h1{font-size:38px;color:#ffda8e;margin:8px 0}h2{font-size:24px;margin:0 0 16px}p{line-height:1.5}.eyebrow{color:#ffda8e;font-size:13px;font-weight:650;letter-spacing:2.2px;margin:0;opacity:.92}section,details{background:#292740;padding:20px;border-radius:22px;margin:20px 0}button,input,select{font:inherit;min-height:52px;padding:13px;border-radius:14px;border:0;width:100%}input,select{background:#fff9ef;color:#19182d;margin:7px 0 16px}button{background:#c2edf0;color:#19182d;cursor:pointer;font-weight:650}button:disabled{opacity:.55;cursor:wait}button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:3px solid #ffda8e;outline-offset:3px}.magic{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:10px 0 16px}.magic button{min-height:88px}.magic span{display:block;font-size:28px;margin-bottom:4px}.fire{background:#ffd0a9}.glitter{background:#e1ceff}.magic button[aria-pressed=true]{box-shadow:inset 0 0 0 3px #ffda8e}.secondary{background:#45415e;color:#fff9ef;margin:12px 0}label{display:block}small{display:block;color:#cecbdf;font-size:14px;line-height:1.6}.status{font-size:15px;color:#d4f3ed;min-height:44px}.notice{background:#36314b;padding:14px;border-radius:14px;font-size:16px}summary{cursor:pointer;font-weight:650;min-height:32px}.parent{padding-top:20px}a{color:#c2edf0;overflow-wrap:anywhere}.check{display:flex;align-items:center;gap:10px;margin-bottom:18px}.check input{width:22px;min-height:22px;margin:0}.check label{font-size:15px}hr{border:0;border-top:1px solid #45415e;margin:22px 0}
</style></head><body>
<p class="eyebrow">THE CARE &amp; TRAINING OF YOUR WALL DRAGON</p><h1>Dragon Kingdom</h1>
<small id="device-firmware" aria-live="polite">Checking installed firmware…</small>
<p id="status" class="status" role="status" aria-live="polite">Waking your dragon…</p>
<p id="setup-internet-warning" class="notice" hidden>This dragon setup Wi-Fi has no internet. Stay connected to control your dragon. Switch to home Wi-Fi or mobile data when you need the internet.</p>
<p id="home-address" class="notice" role="status" aria-live="polite" hidden></p>
<p id="feedback" class="notice" role="status" aria-live="polite" hidden></p>
<p id="busy-status" class="status" role="status" hidden>Please wait for your dragon…</p>
<section aria-labelledby="play-title"><h2 id="play-title">Let's play</h2>
<label for="profile">My profile</label><select id="profile" disabled></select><label for="dragon">My dragon</label><select id="dragon" disabled></select>
<div class="magic" aria-label="Dragon magic">
<button class="glitter" data-effect="glitter" aria-pressed="false"><span aria-hidden="true">✨</span>Glitter</button>
<button class="fire" data-effect="incendio" aria-pressed="false"><span aria-hidden="true">🔥</span>Fire</button>
<button data-effect="breathe" aria-pressed="false"><span aria-hidden="true">🌙</span>Breathe</button>
<button data-effect="colorcycle" aria-pressed="false"><span aria-hidden="true">🌈</span>Rainbow</button></div>
<button id="return" class="secondary">Back to my dragon</button><button id="sleep">Put dragon to sleep</button>
<label for="brightness" style="margin-top:20px">Glow</label><select id="brightness" disabled></select>
<small>Your dragon gently adjusts its glow to the room. Your Glow setting and available power still apply. Use Sleep to turn it off.</small><button id="create-dragon" class="secondary">Make a dragon</button></section>
<section id="editor" hidden><h2>Make or edit your dragon</h2><small>Tap a body part on the dragon, or choose Dragon part below. Pick its colour and magic, then save to see it on your wall. The picture is a colour guide.</small>
<canvas id="preview" width="320" height="320" style="width:100%;max-width:320px;display:block;margin:14px auto 10px;border-radius:16px;touch-action:manipulation" role="img" aria-label="Dragon colour preview. Tap a body part or use Dragon part below."></canvas>
<label for="starting-dragon">Start from</label><select id="starting-dragon"></select><label for="custom-name">Dragon name</label><input id="custom-name" maxlength="32">
<label for="region">Dragon part</label><select id="region"></select>
<label for="region-color">Colour</label><input id="region-color" type="color" style="padding:5px">
<button id="reset-color" class="secondary">Use original colour for this part</button>
<label for="region-effect">Magic on this part</label><select id="region-effect"><option value="keep">Existing magic</option><option value="none">Still</option><option value="0">Rainbow</option><option value="1">Breathe</option><option value="2">Shimmer</option><option value="3">Glitter</option></select>
<button id="save-custom">Save my dragon</button><button id="copy-custom" class="secondary">Save a new copy</button><button id="cancel-custom" class="secondary">Cancel</button><button id="delete-custom" class="secondary" hidden>Delete this custom dragon</button>
</section>
<details id="profile-settings"><summary>My favourites &amp; starting glow</summary><div class="parent"><label for="profile-name">Profile name</label><input id="profile-name" maxlength="32"><label for="profile-glow">Starting glow</label><select id="profile-glow"></select><p id="favorites-help">Choose up to 12 favourites. Patting your dragon cycles through them in the order you choose. The first greets you at startup.</p><p id="favorite-order" class="status"></p><input id="favorite-search" type="search" placeholder="Search dragons by name…" aria-label="Search dragons by name" hidden><small id="favorite-search-status" role="status" aria-live="polite" hidden></small><div id="favorites" style="max-height:280px;overflow:auto"></div><button id="save-profile">Save profile</button><button id="delete-profile" class="secondary" hidden>Delete this profile</button><hr><label for="new-profile-name">New profile name</label><input id="new-profile-name" maxlength="32"><button id="new-profile">Add profile</button></div></details>
<details id="alarm"><summary>Sunrise alarm</summary><div class="parent">
<p>Rooster duty (without the crowing). Your dragon's wings slowly warm the wall from deep ember-orange to morning gold.</p>
<form id="alarm-form"><div class="check"><input id="alarm-enabled" type="checkbox"><label for="alarm-enabled">Wake me every day</label></div>
<label for="alarm-time">Wake-up time</label><input id="alarm-time" type="time" value="07:00" required>
<label for="alarm-duration">Sunrise length (minutes)</label><input id="alarm-duration" type="number" min="1" max="120" step="1" value="20" required>
<small>The sunrise starts this many minutes before your wake-up time. It works while the dragon is asleep and holds its morning glow for 30 minutes afterwards, then returns to your previous lighting.</small>
<button id="save-alarm" style="margin-top:16px" disabled>Save alarm</button></form>
<p id="alarm-status" class="status" role="status" aria-live="polite">Loading alarm…</p>
<button id="preview-alarm" class="secondary">Try a 30-second sunrise</button><button id="stop-alarm" class="secondary" hidden>Stop sunrise</button>
<p id="clock-status" role="status">Clock sync pending. Without home Wi-Fi, open this page after each power loss.</p>
<button id="sync-alarm" class="secondary">Set clock from my phone</button>
<small>Keep your dragon powered for its alarm. Saving borrows your phone's time and daylight-saving rules. After a power cut, it needs internet time or this page opened again. A pat or play button stops the current sunrise.</small>
</div></details>
<details id="rotation"><summary>Automatic dragon rotation</summary><form id="rotation-form">
<label><input id="rotate-enabled" type="checkbox"> Rotate through my active collection</label>
<label for="rotate-seconds">Seconds between dragons (10-86400)</label><input id="rotate-seconds" type="number" min="10" max="86400" value="300" required>
<label for="rotate-order">Order</label><select id="rotate-order"><option value="0">In collection order</option><option value="1">Shuffle</option></select><button>Save rotation</button>
<small>Pauses during sleep and sunrise. Choosing a dragon restarts the interval.</small></form></details>
<details id="parents"><summary>Parent settings · Wi-Fi, backups &amp; updates</summary><div class="parent">
<p>Enter the parent password to deliberately unlock settings. Normal play needs no login.</p>
<form id="parent-login"><label for="parent-password">Parent password</label><input id="parent-password" type="password" autocomplete="current-password" required><button>Unlock parent settings</button></form>
<p id="parent-status" role="status">Parent settings are locked.</p>
<div id="parent-controls" hidden inert><button id="parent-lock" class="secondary">Lock parent settings</button><small>Settings lock after 15 minutes, when you reload the page, or when the dragon restarts.</small>
<h2>Teach your dragon home Wi-Fi</h2><p>Internet is optional. You can always play by touch or while connected directly to your dragon.</p>
<button id="scan" type="button">Find my Wi-Fi</button><p id="scan-status" class="status" role="status"></p>
<form id="wifi"><label for="ssid">Home Wi-Fi name</label><input id="ssid" name="ssid" list="networks" maxlength="32" required autocomplete="off" autocapitalize="none" spellcheck="false"><datalist id="networks"></datalist>
<label for="wifi-password">Wi-Fi password</label><input id="wifi-password" name="password" type="password" maxlength="64" autocomplete="off" autocapitalize="none" spellcheck="false">
<div class="check"><input id="show-password" type="checkbox"><label for="show-password">Show password</label></div>
<button id="connect">Connect my dragon</button><span id="connect-status" role="status" aria-live="polite"></span></form><button id="retry-wifi" class="secondary">Retry home Wi-Fi</button>
<small>Choose a 2.4 GHz network. If your Wi-Fi name doesn't appear, type it yourself. Leave the password blank only for an open network.</small>
<h2 style="margin-top:26px">Open setup Wi-Fi again</h2>
<small>Power cycle your dragon. Its password-protected network opens at every startup. Join it using your setup card and open <a href="http://192.168.4.1/">192.168.4.1</a>, or scan the local-controls QR on the card. Your phone may offer a sign-in page; automatic opening is not guaranteed. Choose to stay connected if it says there is no internet.<br><br>Saved home Wi-Fi is tried for up to 60 seconds. Failure keeps setup Wi-Fi open until you retry. Success closes setup Wi-Fi after 15 seconds, even if your phone is still connected. Join your home Wi-Fi and reopen the home address shown above. A later home-network drop requires a power cycle to reopen setup.</small>
<button id="forget" class="secondary">Forget home Wi-Fi</button><small>This keeps your creations and your dragon's setup-network password (dragon123).</small>
<hr><h2>Backup &amp; restore</h2><p>Backups include collections, creations, sunrise, rotation and light calibration. Wi-Fi and parent passwords are excluded.</p>
<button id="backup">Download backup</button><label for="restore-file">Restore a backup</label><input id="restore-file" type="file" accept="application/json,.json"><button id="restore">Restore selected backup</button>
<h2>Firmware update</h2><p id="update-board" role="status" aria-live="polite">Checking your board type…</p><p>On home Wi-Fi with internet, a parent can check GitHub and approve installation. Your dragon verifies the signed release and downloads it directly. It never installs updates automatically.</p>
<p id="online-prerequisite" class="notice">Direct updates need the dragon connected to home Wi-Fi with internet. Its setup network has no internet.</p>
<p id="firmware-version"></p><label for="update-channel">Firmware channel</label><select id="update-channel"><option value="release">Release (recommended)</option><option value="beta">Beta (experienced users)</option></select><small id="beta-warning" hidden>Beta firmware is experimental. Choose it only if you are comfortable recovering your ESP32 through its internal USB connector. Have the recovery instructions and a computer ready.</small>
<button id="online-check" disabled>Check for updates</button><button id="online-install" hidden>Install signed release</button><button id="online-cancel" class="secondary" hidden>Cancel download</button><p id="online-status" role="status" aria-live="polite">Online updates need home Wi-Fi and a synced clock. File upload works offline.</p><p id="offline-update-help">For an offline update: first use home Wi-Fi or mobile data to download the matching signed .dragon.json package from <a href="https://github.com/sai021/dragon-kingdom/releases" target="_blank" rel="noopener">GitHub releases</a> on your phone or PC. Then join the dragon network again, reopen this page, unlock Parent settings and select the saved file below. Uploading that file needs no internet. Keep power connected throughout the update.</p>
<label for="update-file">Signed firmware package</label><input id="update-file" type="file" accept="application/json,.json"><button id="update">Install firmware</button><p id="update-status" role="status"></p>
<button id="reset-device" class="secondary">Reset all saved data</button>
<small>USB recovery: disconnect the bottom product USB-C power cable before connecting laptop USB. Remove one screw to access the internal ESP32 USB. The bottom USB-C port is power-only. Never connect laptop USB and external/main power simultaneously.</small>
</div></div></details>
<script>
const $=selector=>document.querySelector(selector),effects=['zones','breathe','colorcycle','glitter','incendio','leviosa'];
let parentToken="",onlineState=null,parentExpiry=0,parentTimer;
const firmwareBoards={s3:{name:'ESP32-S3',file:'dragon-s3.dragon.json'},c3:{name:'ESP32-C3',file:'dragon-c3.dragon.json'}};
async function loadUpdateBoard(){const token=parentToken;try{const target=await request('/api/update'),board=firmwareBoards[target.board];if(parentToken!==token)return;if(!board)throw Error('Board type could not be identified. Reload before choosing firmware.');$('#update-board').textContent='Detected board: '+board.name+'. Download '+board.file+' for file upload. Direct updates select the matching version automatically.'}catch(error){if(parentToken===token)$('#update-board').textContent='Could not check board type: '+error.message}}
function lockParent(message="Parent settings are locked."){parentToken="";parentExpiry=0;$("#update-channel").value="release";$("#beta-warning").hidden=true;onlineState=null;$("#update-board").textContent="Checking your board type…";clearTimeout(parentTimer);$("#parent-controls").hidden=true;$("#parent-controls").inert=true;$("#parent-login").hidden=false;$("#parent-password").value="";$("#parent-status").textContent=message;}
function unlockParent(token){parentToken=token;parentExpiry=Date.now()+15*60*1000;$("#parent-controls").hidden=false;$("#parent-controls").inert=false;$("#parent-login").hidden=true;$("#parent-password").value="";$("#parent-status").textContent="Parent settings unlocked.";clearTimeout(parentTimer);parentTimer=setTimeout(()=>lockParent("Parent session expired. Enter the password again."),15*60*1000);loadUpdateBoard();}
let loading=false,commandBusy=false,scanBusy=false,pollTimer,lastState=null,alarmState=null,alarmFieldsLoaded=false,alarmLoading=false;
function phoneClock(){
 const epoch=Math.floor(Date.now()/1000),validFrom=epoch-86400,validUntil=epoch+400*86400;
 const offsetAt=seconds=>-new Date(seconds*1000).getTimezoneOffset();
 const data={epoch,validFrom,validUntil,offset:offsetAt(validFrom),count:0};
 let previous=validFrom,offset=data.offset;
 for(let sample=validFrom+86400;sample<=validUntil;sample+=86400){
  const next=offsetAt(sample);if(next!==offset){
   let low=previous,high=sample;while(high-low>1){const middle=Math.floor((low+high)/2);if(offsetAt(middle)===offset)low=middle;else high=middle}
   if(data.count>=4)throw Error('Could not read your time zone. Check your phone clock.');
   data['at'+data.count]=high;data['offset'+data.count]=next;data.count++;offset=next;
  }previous=sample;
 }
 return data;
}
function renderAlarm(state,fields=false){
 alarmState=state;
 if(fields){alarmFieldsLoaded=true;$('#alarm-enabled').checked=state.enabled;$('#alarm-time').value=String(Math.floor(state.minute/60)).padStart(2,'0')+':'+String(state.minute%60).padStart(2,'0');$('#alarm-duration').value=state.duration}
 $('#stop-alarm').hidden=!state.active;
 if(state.active){$('#sleep').textContent='Stop sunrise';for(const button of document.querySelectorAll('[data-effect]'))button.setAttribute('aria-pressed','false')}
 $('#alarm-status').textContent=state.active?(state.preview?'Preview sunrise':'Sunrise')+' · '+state.progress+'% glow':!state.clockReady?'Clock needs setting. Open this page or tap Set clock from my phone.':state.enabled?'Daily sunrise saved. Your dragon is ready for wake-up.':'Daily alarm is off. You can still try a sunrise.';
}
function updateControls(){
 const ready=Boolean(collection),playable=ready&&visibleDragons().length>0;
 for(const node of document.querySelectorAll('[data-effect],#return,#sleep,#brightness,#dragon'))node.disabled=commandBusy||!playable;
 for(const id of ['profile','profile-glow','save-profile','new-profile','new-profile-name','delete-profile','create-dragon','forget'])$('#'+id).disabled=commandBusy||!ready;
 $('#profile-name').disabled=commandBusy||!ready||collection.active===0;
 for(const id of ['save-custom','copy-custom','delete-custom','cancel-custom','starting-dragon','region','region-color','region-effect','reset-color','custom-name'])$('#'+id).disabled=commandBusy||!draft;
 for(const id of ['preview-alarm','stop-alarm','sync-alarm'])$('#'+id).disabled=commandBusy||alarmLoading||!ready;
 $('#save-alarm').disabled=commandBusy||alarmLoading||!alarmFieldsLoaded;
 for(const id of ['alarm-enabled','alarm-time','alarm-duration'])$('#'+id).disabled=commandBusy||!alarmFieldsLoaded;
 $('#scan').disabled=$('#connect').disabled=commandBusy||scanBusy||Boolean(lastState?.connecting);
 $('#online-check').disabled=commandBusy||Boolean(onlineState?.busy)||(!lastState?.connected||Boolean(lastState?.accessPoint));
 $('#online-install').disabled=commandBusy||(!lastState?.connected||Boolean(lastState?.accessPoint));
 $('#online-prerequisite').textContent=lastState?.connected&&!lastState?.accessPoint?'Your dragon is on home Wi-Fi. Direct updates require internet access on that network.':'Direct updates are unavailable on the dragon setup network. Connect the dragon to home Wi-Fi with internet, or download a file before joining setup Wi-Fi and upload it offline.';
 document.body.setAttribute('aria-busy',String(commandBusy));$('#busy-status').hidden=!commandBusy;
}
function setCommandBusy(value){commandBusy=value;updateControls()}
async function loadAlarm(){
 alarmLoading=true;updateControls();
 try{renderAlarm(await request('/api/alarm'),true);renderAlarm(await request('/api/alarm/clock',phoneClock()));$('#clock-status').textContent='Clock synced from your phone.';updateControls()}
 catch(error){$('#alarm-status').textContent='Could not load the alarm. '+error.message}finally{alarmLoading=false;updateControls()}
}
async function alarmAction(path,data){
 if(commandBusy||alarmLoading)return;setCommandBusy(true);$('#save-alarm').disabled=true;
 try{renderAlarm(await request(path,data),!alarmFieldsLoaded);feedback('')}
 catch(error){$('#alarm-status').textContent=error.message}
 finally{setCommandBusy(false);updateControls()}
}
function feedback(message){$('#feedback').hidden=!message;$('#feedback').textContent=message}
async function request(path,data){
 if(parentToken&&Date.now()>=parentExpiry)lockParent("Parent session expired. Enter the password again.");
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),8000);
 try{const options={signal:controller.signal,cache:'no-store',headers:parentToken?{'X-Dragon-Parent':parentToken}:{}};if(data){options.method='POST';options.headers={...options.headers,'X-Dragon-Request':'1'};options.body=new URLSearchParams(data)}const response=await fetch(path,options);if(response.status===401){lockParent('Parent settings are locked. Enter your password to continue.')}if(!response.ok)throw Error(await response.text());return await response.json()}finally{clearTimeout(timer)}
}
function render(state){
 const board=firmwareBoards[state.board];$('#device-firmware').textContent=state.firmware?'Firmware '+state.firmware+(board?' · '+board.name:''):'Firmware version unavailable. Reconnect to your dragon.';
 $('#setup-internet-warning').hidden=!state.accessPoint;$('#setup-internet-warning').textContent=state.connected?'Your dragon joined home Wi-Fi and its setup network is closing. Rejoin home Wi-Fi to continue with internet access.':'This dragon setup Wi-Fi has no internet. Stay connected to control your dragon. Switch to home Wi-Fi or mobile data when you need the internet.';
 if(lastState&&state.profile!==undefined&&state.profile!==lastState.profile)reloadCollection();lastState=state;$('#status').textContent=state.connecting?'Connecting to home Wi-Fi…':state.connected?'Your dragon is on home Wi-Fi. Ready to play!':state.accessPoint?'Connected directly to your dragon. Ready to play!':'Home Wi-Fi is unavailable. Touch play still works.';
 if(document.activeElement!==$('#dragon')&&Array.from($('#dragon').options).some(option=>option.value===String(state.dragon)))$('#dragon').value=state.dragon;if(document.activeElement!==$('#brightness'))$('#brightness').value=state.brightness;
 const asleep=state.mode===9||state.brightness===0;$('#sleep').textContent=asleep?'Wake my dragon':'Put dragon to sleep';
 for(const button of document.querySelectorAll('[data-effect]'))button.setAttribute('aria-pressed',String(!asleep&&effects[state.mode]===button.dataset.effect));
 if(typeof updateCreateButtonLabel==='function')updateCreateButtonLabel();
 updateControls();
 $('#connect-status').textContent=state.connecting?'Connecting… up to 60 seconds. Your phone may briefly disconnect during a radio channel change.':state.connected?'Connected successfully. Setup Wi-Fi closes shortly; join home Wi-Fi and open the address above.':state.message;
 if(state.message.startsWith('Could not')||state.message.includes('could not be saved'))feedback(state.message);
 if(state.connected){const hostname='http://'+state.hostname+'.local/',ip='http://'+state.ip+'/';try{sessionStorage.setItem('dragon-home',JSON.stringify({hostname,ip}))}catch(e){}showHomeAddress({hostname,ip})}
}
function showHomeAddress(home){
 const box=$('#home-address');if(box.dataset.hostname===home.hostname&&box.dataset.ip===home.ip&&!box.hidden)return;
 box.dataset.hostname=home.hostname;box.dataset.ip=home.ip;box.hidden=false;
 box.replaceChildren(document.createTextNode('On home Wi-Fi, open and bookmark: '));
 const link=document.createElement('a');link.textContent=home.hostname;link.href=home.hostname;box.append(link);
 box.append(document.createElement('br'),document.createTextNode('If that does not open, try: '));
 const fallback=document.createElement('a');fallback.textContent=home.ip;fallback.href=home.ip;box.append(fallback);
 box.append(document.createElement('br'),document.createTextNode('Rejoin your home Wi-Fi first. The bookmark name stays the same if the router changes the numeric address.'));
}
async function refresh(){
 if(loading||commandBusy)return;loading=true;
 try{render(await request('/api/state'));if(parentToken)try{renderOnline(await request('/api/update/online'))}catch(e){$('#online-status').textContent=e.message}if(alarmFieldsLoaded)renderAlarm(await request('/api/alarm'));else await loadAlarm()}catch(error){$('#status').textContent='Connection lost. If joining Wi-Fi, wait up to 60 seconds: a channel change can briefly disconnect your phone. On success join home Wi-Fi and open the saved address; on failure rejoin the dragon network. Power cycle to reopen setup Wi-Fi.';try{const home=JSON.parse(sessionStorage.getItem('dragon-home'));if(home)showHomeAddress(home)}catch(e){}}finally{loading=false}
}
async function play(action,value){if(commandBusy)return;setCommandBusy(true);feedback('');try{await request('/api/play',{action,value});render(await request('/api/state'))}catch(error){feedback('Could not reach your dragon. '+error.message)}finally{setCommandBusy(false)}}
$('#dragon').onchange=event=>play('dragon',event.target.value);$('#brightness').onchange=event=>play('brightness',event.target.value);
for(const button of document.querySelectorAll('[data-effect]'))button.onclick=()=>play('effect',button.dataset.effect);
$('#return').onclick=()=>play('effect','zones');$('#sleep').onclick=()=>play('toggle','1');$('#show-password').onchange=event=>$('#wifi-password').type=event.target.checked?'text':'password';
$('#alarm-form').onsubmit=event=>{event.preventDefault();const [hour,minute]=$('#alarm-time').value.split(':').map(Number);alarmAction('/api/alarm',{...phoneClock(),enabled:$('#alarm-enabled').checked?1:0,minute:hour*60+minute,duration:$('#alarm-duration').value})};
$('#preview-alarm').onclick=()=>alarmAction('/api/alarm/preview',{});$('#stop-alarm').onclick=()=>alarmAction('/api/alarm/stop',{});$('#sync-alarm').onclick=()=>alarmAction('/api/alarm/clock',phoneClock());
$('#wifi').onsubmit=async event=>{event.preventDefault();if(commandBusy||lastState?.connecting)return;setCommandBusy(true);feedback('');$('#connect').disabled=true;try{await request('/api/wifi',Object.fromEntries(new FormData(event.target)));$('#wifi-password').value='';render(await request('/api/state'))}catch(error){feedback(error.message)}finally{setCommandBusy(false);$('#connect').disabled=Boolean(lastState?.connecting)}};
$('#scan').onclick=async()=>{
 if(commandBusy||scanBusy)return;scanBusy=true;updateControls();$('#scan').disabled=true;$('#connect').disabled=true;$('#scan-status').textContent='Looking for nearby Wi-Fi…';
 try{await request('/api/scan',{});let results;for(let attempt=0;attempt<20;attempt++){results=await request('/api/scan');if(!results.scanning)break;await new Promise(resolve=>setTimeout(resolve,500))}if(results.scanning)throw Error('The search took too long. Try again, or type your network name.');$('#networks').replaceChildren();for(const network of results.networks){const option=document.createElement('option');option.value=network.name;$('#networks').append(option)}$('#scan-status').textContent=results.networks.length?'Tap the Wi-Fi name box to choose your network.':'No networks found. You can type the name yourself.';$('#ssid').focus()}catch(error){$('#scan-status').textContent=error.message}finally{scanBusy=false;updateControls()}
};
$('#forget').onclick=async()=>{if(commandBusy||!confirm('Forget home Wi-Fi? Power cycle afterwards to open the dragon network.'))return;setCommandBusy(true);try{await request('/api/forget-wifi',{});feedback('Home Wi-Fi forgotten. Power cycle, then join the dragon network using your setup card.');$('#home-address').hidden=true;try{sessionStorage.removeItem('dragon-home')}catch(e){}}catch(error){feedback(error.message)}finally{setCommandBusy(false)}};
async function initialize(){
 try{const dragons=await request('/api/dragons?catalog=1');await loadLibrary(dragons);$('#brightness').replaceChildren();for(let value=0;value<=100;value+=10){const option=document.createElement('option');option.value=value;option.textContent=value?value+'%':'Off';$('#brightness').append(option)}updateControls();await loadAlarm();await refresh();try{const r=await request('/api/rotation');$('#rotate-enabled').checked=Boolean(r.enabled);$('#rotate-seconds').value=r.seconds;$('#rotate-order').value=r.shuffle}catch(e){}}catch(error){feedback('Could not load your dragons. Reconnect and refresh this page.')}
 clearTimeout(pollTimer);pollTimer=setTimeout(async function poll(){await refresh();if(!collection)await initialize();else pollTimer=setTimeout(poll,3000)},3000);
}
$('#parent-login').onsubmit=async e=>{e.preventDefault();try{const result=await request('/api/parent/login',{password:$('#parent-password').value});unlockParent(result.token)}catch(error){lockParent(error.message)}};
$('#parent-lock').onclick=async()=>{const logout=request('/api/parent/logout',{});lockParent();try{await logout}catch(e){}};
$('#retry-wifi').onclick=async()=>{try{await request('/api/wifi/retry',{});await refresh()}catch(error){feedback(error.message)}};
$('#rotation-form').onsubmit=async e=>{e.preventDefault();try{await request('/api/rotation',{enabled:$('#rotate-enabled').checked?1:0,shuffle:$('#rotate-order').value,seconds:$('#rotate-seconds').value});feedback('Rotation saved.')}catch(error){feedback(error.message)}};
function downloadJson(value,name){const url=URL.createObjectURL(new Blob([JSON.stringify(value)],{type:'application/json'}));const link=document.createElement('a');link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
$('#backup').onclick=async()=>{try{downloadJson(await request('/api/backup'),'dragon-backup.json')}catch(error){feedback(error.message)}};
$('#restore').onclick=async()=>{try{const file=$('#restore-file').files[0];if(!file)throw Error('Choose a backup first.');if(file.size>12000)throw Error('Backup is too large.');const value=JSON.parse(await file.text());if(value.format!=='dragon-backup-v1')throw Error('Unsupported backup format.');if(!confirm('Replace collections, creations and settings with this backup?'))return;await request('/api/restore',{data:value.data});feedback('Restore staged. Dragon is restarting; reconnect after startup.')}catch(error){feedback(error.message)}};
$('#reset-device').onclick=async()=>{if(prompt('This deletes collections, creations, settings and saved home Wi-Fi. Type RESET to continue.')!=='RESET')return;try{await request('/api/reset',{confirm:'RESET'});lockParent();feedback('Reset staged. Reconnect after restart. The parent password remains dragon123.')}catch(error){feedback(error.message)}};
$('#update').onclick=async()=>{
 if(commandBusy)return;setCommandBusy(true);const status=$('#update-status');
 try{const file=$('#update-file').files[0];if(!file)throw Error('Choose a signed firmware package first.');if(file.size>3200000)throw Error('Firmware package is too large.');const pkg=JSON.parse(await file.text());if(pkg.format!==1||typeof pkg.image!=='string'||pkg.image.length!==pkg.size*2||!/^[0-9a-f]+$/.test(pkg.image))throw Error('Invalid firmware package.');
 const target=await request('/api/update');if(!firmwareBoards[target.board])throw Error('Board type could not be identified. Reload before choosing firmware.');if(pkg.board!==target.board)throw Error('Wrong board package. Your '+firmwareBoards[target.board].name+' needs '+firmwareBoards[target.board].file+'.');
 await request('/api/update/start',{board:pkg.board,size:pkg.size,sha256:pkg.sha256,signature:pkg.signature});
 for(let offset=0;offset<pkg.size;offset+=512){const result=await request('/api/update/chunk',{offset,data:pkg.image.slice(offset*2,(offset+512)*2)});status.textContent='Uploading: '+Math.floor(result.offset*100/pkg.size)+'%. Keep power connected.'}
 await request('/api/update/finish',{});lockParent();feedback('Firmware verified. Restarting; reconnect after one minute.');status.textContent='Verified. Restarting and checking startup. Reconnect after one minute; failed startup rolls back automatically.';
 }catch(error){status.textContent=error.message;try{await request('/api/update/abort',{})}catch(e){}}finally{setCommandBusy(false)}
};
function renderOnline(state){$('#firmware-version').textContent='Installed firmware: '+state.current;if(state.channel&&state.channel!==$('#update-channel').value)return;onlineState=state;$('#update-channel').disabled=state.busy||commandBusy;$('#online-status').textContent=state.message+(state.phase===4?' '+state.progress+'%':'');$('#online-install').hidden=state.phase!==2;$('#online-install').textContent='Install '+(state.release||'signed release');$('#online-check').disabled=state.busy||commandBusy||(!lastState?.connected||Boolean(lastState?.accessPoint));$('#online-install').disabled=commandBusy||(!lastState?.connected||Boolean(lastState?.accessPoint));$('#online-cancel').hidden=!state.busy;$('#update').disabled=state.busy}
async function onlineAction(path,data){if(commandBusy)return;try{renderOnline(await request(path,data))}catch(error){$('#online-status').textContent=error.message}}
$('#update-channel').onchange=()=>{$('#beta-warning').hidden=$('#update-channel').value!=='beta';$('#online-install').hidden=true;onlineState=null;$('#online-status').textContent='Channel changed. Check for updates before installing.'};
$('#online-check').onclick=()=>onlineAction('/api/update/online/check',{channel:$('#update-channel').value});
$('#online-install').onclick=()=>{if(onlineState&&confirm('Install '+onlineState.release+'? Keep power connected. Your dragon will restart.'))onlineAction('/api/update/online/install',{release:onlineState.release})};
$('#online-cancel').onclick=()=>onlineAction('/api/update/online/cancel',{});
initialize();
</script>
<script>
let collection=null,catalog=[],favorites=[],draft=null,reloading=false;
function collectionRequest(path,data,context=collection){
 return request(path,{...data,profile:context.active??context.profile,generation:context.generation});
}
const regionNames=['Background','Left wing edge','Right wing edge','Left horn','Right horn','Face','Body','Tail','Left wing','Right wing'];
const dragonShapeData={
 8:"M143,5L146,6L134,11L126,19L122,23L117,37L113,39L110,43L107,54L108,58L106,63L106,74L110,88L92,80L86,80L84,82L84,85L89,99L89,103L87,108L87,114L91,117L95,117L106,111L107,112L106,125L103,135L103,144L106,153L112,159L118,162L131,165L133,168L133,176L124,197L124,202L122,203L121,209L119,213L112,212L106,216L101,226L101,234L98,237L92,237L78,241L70,245L62,252L55,245L50,242L43,242L40,243L37,246L36,250L35,262L32,259L23,245L16,229L12,215L9,196L9,166L10,157L13,142L22,115L34,92L44,77L58,61L71,48L88,33L105,22L120,14Z",
 9:"M179,7L181,7L195,12L218,24L238,39L255,54L266,66L282,86L294,107L299,118L307,143L310,158L311,167L311,195L309,210L302,234L294,250L282,266L281,264L283,256L282,248L280,243L275,241L270,243L268,246L260,256L250,267L251,257L248,245L243,241L237,241L228,248L227,240L224,237L219,236L219,228L216,220L211,215L202,212L192,190L187,172L189,166L203,162L208,159L215,151L217,144L217,135L214,125L212,112L213,111L222,116L229,116L232,115L233,111L232,100L236,88L236,83L234,80L227,80L213,84L215,75L215,62L212,45L208,39L203,35L202,29L197,21L190,13Z",
 1:"M140,3L150,4L140,6L120,14L100,25L78,42L58,61L44,77L34,92L22,115L17,128L13,142L9,165L9,195L10,204L14,222L21,241L32,259L39,266L43,274L41,275L26,260L18,250L13,241L9,231L3,209L0,185L0,166L3,145L11,117L22,94L34,75L45,62L62,44L75,32L98,17L119,8L130,5Z",
 2:"M169,3L179,3L190,5L212,12L231,22L248,35L273,59L283,70L298,93L309,116L316,139L320,164L320,184L317,208L310,233L303,248L290,265L279,275L277,274L281,266L288,259L299,241L305,225L310,203L311,194L311,167L310,158L307,143L299,118L287,94L275,76L255,54L244,44L230,32L213,21L195,12Z",
 7:"M98,236L101,236L102,237L102,244L104,249L104,253L86,257L79,264L77,267L77,277L78,281L82,288L88,293L99,299L121,304L141,304L161,297L170,297L187,303L191,303L192,305L182,312L176,315L169,317L156,317L148,315L141,311L129,313L116,313L99,311L87,308L73,301L67,295L59,283L56,270L56,266L58,258L62,253L70,245L85,239Z",
 6:"M133,166L161,173L187,166L188,177L192,190L202,213L207,213L211,216L215,219L218,225L219,230L219,242L217,249L212,256L218,264L218,271L215,274L212,275L203,275L193,272L183,277L173,277L165,273L155,273L146,277L139,278L135,277L130,275L127,271L118,274L114,274L111,271L106,273L103,272L102,268L104,262L107,260L107,257L102,244L101,234L102,223L107,214L112,212L119,213L120,212L131,184L133,177Z",
 5:"M160,45L163,47L167,59L170,55L173,54L175,56L177,62L188,68L189,69L186,72L186,75L189,79L197,87L202,88L227,80L233,80L235,82L236,84L236,88L232,99L233,106L232,112L228,116L223,116L218,115L213,111L212,112L217,136L217,144L212,154L208,159L200,163L162,173L118,162L111,158L108,154L104,149L103,142L106,130L107,112L105,111L100,115L93,117L89,115L87,112L87,109L89,103L89,95L85,84L85,81L91,80L96,81L111,89L114,86L119,88L125,86L130,81L134,76L134,72L132,68L139,64L145,63L145,57L148,53L150,54L154,58L157,48Z",
 3:"M114,37L117,37L119,40L119,49L122,58L127,64L134,72L134,76L130,81L125,86L119,88L115,86L111,82L108,71L108,52L110,43Z",
 4:"M203,37L206,37L208,40L211,45L213,56L213,63L212,73L210,80L205,86L201,88L194,84L188,79L186,73L187,71L195,63L200,54L202,45L202,39Z"
};
const drawOrder=[8,9,1,2,7,6,5,3,4],hitOrder=[3,4,5,6,7,1,2,8,9];
const zoneCenters={1:[18,118],2:[302,118],3:[118,66],4:[202,66],5:[160,115],6:[160,228],7:[120,308],8:[65,153],9:[254,153]};
const effectIcons=['🌈','🌙','💫','✨'];
const shapePaths=typeof Path2D==='function'?Object.fromEntries(Object.entries(dragonShapeData).map(([z,d])=>[Number(z),new Path2D(d)])):null;

function updateCreateButtonLabel(){
 const btn=$('#create-dragon');if(!btn||!catalog.length)return;
 const current=catalog.find(d=>String(d.id)===$('#dragon').value);
 btn.textContent=current?.custom?'Edit or copy custom dragon':'Make a dragon';
}
async function loadLibrary(dragons){
 catalog=dragons;collection=await request('/api/library');
 $('#profile').replaceChildren();for(const p of collection.profiles){const o=document.createElement('option');o.value=p.id;o.textContent=p.name;$('#profile').append(o)}$('#profile').value=collection.active;$('#profile').disabled=false;
 const p=collection.profiles.find(p=>p.id===collection.active);$('#profile-name').value=p.name;$('#profile-name').disabled=collection.active===0;$('#delete-profile').hidden=collection.active===0;$('#favorites-help').textContent=collection.active===0?'All (The Great Sanctuary) contains every dragon and cannot be renamed or deleted.':'Choose up to 12 favourites. Your roost shows these plus your own creations. Patting cycles through your roost. Uncheck and recheck to move a favourite to the end.';favorites=[...p.favorites];
 $('#profile-glow').replaceChildren();for(let n=10;n<=100;n+=10){const o=document.createElement('option');o.value=n;o.textContent=n+'%';$('#profile-glow').append(o)}$('#profile-glow').value=p.brightness;
 const isAll=collection.active===0;$('#favorites').hidden=isAll;if($('#favorite-search')){$('#favorite-search').hidden=isAll;$('#favorite-search').value='';$('#favorite-search-status').hidden=true;$('#favorite-search-status').textContent=''}
 $('#favorites').replaceChildren();for(const dragon of catalog){const row=document.createElement('div');row.className='check';row.dataset.name=dragon.name.toLowerCase();const input=document.createElement('input');input.type='checkbox';input.id='favorite-'+dragon.id;input.checked=favorites.includes(dragon.id);const label=document.createElement('label');label.htmlFor=input.id;label.textContent=dragon.name+(dragon.custom?(dragon.owned?' · made by you':' · custom dragon'):'');row.append(input,label);$('#favorites').append(row);input.onchange=()=>{if(input.checked){if(favorites.length>=12){input.checked=false;feedback('Choose up to 12 favourites.');return}favorites.push(dragon.id)}else favorites=favorites.filter(id=>id!==dragon.id);showFavoriteOrder()}}
 showFavoriteOrder();populateDragons();updateCreateButtonLabel();updateControls();
}
$('#favorite-search').oninput=event=>{
 const q=event.target.value.trim().toLowerCase();let matches=0;
 for(const row of document.querySelectorAll('#favorites .check')){row.hidden=Boolean(q&&!row.dataset.name.includes(q));if(!row.hidden)matches++}
 const status=$('#favorite-search-status');status.hidden=!q;
 status.textContent=matches?(matches===1?'1 dragon matches.':matches+' dragons match.'):'No dragons match your search.';
};
function visibleDragons(){if(collection.active===0)return catalog;const selected=collection.profiles.find(p=>p.id===collection.active).favorites.map(id=>catalog.find(d=>d.id===id)).filter(Boolean);return [...selected,...catalog.filter(d=>d.custom&&d.owned&&!selected.some(s=>s.id===d.id))]}
function populateDragons(){const dragons=visibleDragons();$('#dragon').replaceChildren();if(!dragons.length){const o=document.createElement('option');o.value='';o.textContent='Add favourites or make a dragon';$('#dragon').append(o)}for(const d of dragons){const o=document.createElement('option');o.value=d.id;o.textContent=d.name+(d.custom?' ✨':'');$('#dragon').append(o)}$('#dragon').disabled=!dragons.length;for(const button of document.querySelectorAll('[data-effect],#return,#sleep,#brightness'))button.disabled=!dragons.length;if(lastState&&dragons.some(d=>d.id===lastState.dragon))$('#dragon').value=lastState.dragon;else if(dragons.length)$('#dragon').value=dragons[0].id;updateCreateButtonLabel();updateControls()}
function showFavoriteOrder(){$('#favorite-order').textContent=collection.active===0?'All dragons':favorites.length?favorites.map((id,i)=>(i+1)+'. '+catalog.find(d=>d.id===id)?.name).join(' · '):'No favourites yet. Your own creations appear automatically.'}
async function reloadCollection(){if(reloading)return;reloading=true;try{await loadLibrary(await request('/api/dragons?catalog=1'))}catch(e){feedback(e.message)}finally{reloading=false}}
function closeEditor(){draft=null;$('#editor').hidden=true}
$('#profile').onchange=async event=>{
 const id=event.target.value;if(draft&&!confirm('Switch profiles and discard your unsaved dragon?')){event.target.value=collection.active;return}
 if(commandBusy){event.target.value=collection.active;return}setCommandBusy(true);try{await collectionRequest('/api/profile',{action:'select',id});closeEditor();lastState=null;await reloadCollection();render(await request('/api/state'));feedback('Profile selected.')}catch(e){event.target.value=collection.active;feedback(e.message)}finally{setCommandBusy(false)}
};
$('#save-profile').onclick=async()=>{if(commandBusy)return;setCommandBusy(true);try{await collectionRequest('/api/profile',{action:'update',name:$('#profile-name').value,brightness:$('#profile-glow').value,favorites:favorites.join(',')});await reloadCollection();render(await request('/api/state'));feedback('Profile saved.')}catch(e){feedback(e.message)}finally{setCommandBusy(false)}};
$('#new-profile').onclick=async()=>{if(commandBusy)return;if(draft&&!confirm('Create a profile and discard your unsaved dragon?'))return;setCommandBusy(true);try{await collectionRequest('/api/profile',{action:'create',name:$('#new-profile-name').value,brightness:100,favorites:''});closeEditor();lastState=null;await reloadCollection();render(await request('/api/state'));$('#new-profile-name').value='';feedback('Your new profile is ready.')}catch(e){feedback(e.message)}finally{setCommandBusy(false)}};

function zoneDisplayColor(z){
 if(draft.colorMask&(1<<z))return draft.colors[z];
 // Approximate the original markings without changing their saved pixel data.
 const pixels=draft.originalPixels.filter((_,i)=>draft.zones[i]===z);
 if(!pixels.length)return draft.originalColors[z];
 const rgb=[0,0,0];for(const color of pixels)for(let c=0;c<3;c++)rgb[c]+=parseInt(color.slice(1+c*2,3+c*2),16);
 return '#'+rgb.map(sum=>Math.round(sum/pixels.length).toString(16).padStart(2,'0')).join('');
}
function drawDraft(){
 if(!draft)return;const ctx=$('#preview').getContext('2d'),selected=Number($('#region').value);
 ctx.fillStyle='#19182d';ctx.fillRect(0,0,320,320);
 if(!shapePaths){ctx.fillStyle='#fff9ef';ctx.font='16px system-ui,sans-serif';ctx.textAlign='center';ctx.fillText('Choose a Dragon part below',160,160);return}
 ctx.save();
 for(const z of drawOrder){
  const path=shapePaths[z];if(!path)continue;
  ctx.fillStyle=zoneDisplayColor(z);ctx.fill(path);
  ctx.strokeStyle='#19182d';ctx.lineWidth=4.5;ctx.lineJoin='round';ctx.stroke(path);
  ctx.strokeStyle='rgba(255,249,239,0.55)';ctx.lineWidth=1.4;ctx.stroke(path);
 }
 if(shapePaths[selected]){ctx.strokeStyle='#ffda8e';ctx.lineWidth=3.5;ctx.stroke(shapePaths[selected])}
 ctx.font='14px system-ui,sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
 for(const z of drawOrder){
  const active=draft.effectZones.map((mask,i)=>mask&(1<<z)?i:null).filter(i=>i!==null);
  if(active.length===1&&zoneCenters[z]){const [x,y]=zoneCenters[z];ctx.fillText(effectIcons[active[0]],x,y)}
 }
 ctx.restore();
}
function showRegion(){if(!draft)return;const z=Number($('#region').value);$('#region-color').value=zoneDisplayColor(z);const active=draft.effectZones.map((mask,i)=>mask&(1<<z)?i:null).filter(i=>i!==null);$('#region-effect').value=active.length===0?'none':active.length===1?String(active[0]):'keep';drawDraft()}
async function editDragon(id){
 if(commandBusy)return;if(draft&&!confirm('Discard your unsaved changes and start again?'))return;
 setCommandBusy(true);try{const detail=await request('/api/dragon-detail?id='+id),base=detail.id===detail.base?detail:await request('/api/dragon-detail?id='+detail.base);if(detail.profile!==base.profile||detail.generation!==base.generation)throw Error('Your collection changed. Reload the page before editing.');draft={...detail,originalPixels:base.pixels,originalColors:base.colors};$('#custom-name').value=detail.id===detail.base?'My '+detail.name:detail.name;$('#region').replaceChildren();for(let i=0;i<regionNames.length;i++){if(!detail.zones.includes(i))continue;const o=document.createElement('option');o.value=i;o.textContent=regionNames[i];$('#region').append(o)}$('#region').value=5;$('#copy-custom').hidden=$('#delete-custom').hidden=!detail.canEdit;$('#starting-dragon').replaceChildren();for(const d of catalog){const o=document.createElement('option');o.value=d.id;o.textContent=d.name;$('#starting-dragon').append(o)}$('#starting-dragon').value=detail.id;$('#editor').hidden=false;showRegion();$('#editor').scrollIntoView({behavior:'smooth',block:'start'});feedback('')}catch(e){feedback(e.message)}finally{setCommandBusy(false)}
};
$('#create-dragon').onclick=()=>editDragon($('#dragon').value===''?catalog[0].id:$('#dragon').value);
$('#starting-dragon').onchange=e=>editDragon(e.target.value);
$('#region').onchange=showRegion;
$('#preview').onclick=event=>{
 if(!draft||!shapePaths)return;
 const canvas=event.currentTarget,bounds=canvas.getBoundingClientRect();
 const x=(event.clientX-bounds.left)/bounds.width*320,y=(event.clientY-bounds.top)/bounds.height*320;
 const ctx=canvas.getContext('2d');
 for(const z of hitOrder)if(shapePaths[z]&&draft.zones.includes(z)&&ctx.isPointInPath(shapePaths[z],x,y)){$('#region').value=z;showRegion();return}
};
$('#region-color').oninput=event=>{if(!draft)return;const z=Number($('#region').value);draft.colorMask|=1<<z;draft.colors[z]=event.target.value;drawDraft()};
$('#reset-color').onclick=()=>{if(!draft)return;const z=Number($('#region').value);draft.colorMask&=~(1<<z);draft.colors[z]=draft.originalColors[z];showRegion()};
$('#region-effect').onchange=event=>{if(!draft||event.target.value==='keep')return;const bit=1<<Number($('#region').value);draft.effectZones=draft.effectZones.map(mask=>mask&~bit);if(event.target.value!=='none')draft.effectZones[Number(event.target.value)]|=bit;showRegion()};
async function saveCustom(copy){
 if(!draft||commandBusy)return;setCommandBusy(true);
 try{await collectionRequest('/api/custom',{id:copy||!draft.canEdit?-1:draft.id,base:draft.base,name:$('#custom-name').value,colorMask:draft.colorMask,colors:draft.colors.map(c=>c.slice(1)).join(''),effectZones:draft.effectZones.join(',')},draft);closeEditor();await reloadCollection();render(await request('/api/state'));feedback('Your dragon is saved!')}catch(e){feedback(e.message)}finally{setCommandBusy(false)}
}
$('#save-custom').onclick=()=>saveCustom(false);$('#copy-custom').onclick=()=>saveCustom(true);$('#cancel-custom').onclick=()=>{closeEditor();feedback('Changes cancelled.')};
$('#delete-custom').onclick=async()=>{if(!draft||commandBusy||!confirm('Delete this custom dragon? The supplied dragons are always kept.'))return;setCommandBusy(true);try{await collectionRequest('/api/delete-custom',{id:draft.id},draft);closeEditor();await reloadCollection();render(await request('/api/state'));feedback('Custom dragon deleted.')}catch(e){feedback(e.message)}finally{setCommandBusy(false)}};

$('#delete-profile').onclick=async()=>{if(commandBusy||!collection.active||!confirm('Delete this profile? Its custom dragons will be kept in All.'))return;setCommandBusy(true);try{await collectionRequest('/api/delete-profile',{id:collection.active});closeEditor();lastState=null;await reloadCollection();render(await request('/api/state'));feedback('Profile deleted. Its creations are in All.')}catch(e){feedback(e.message)}finally{setCommandBusy(false)}};

// Apply availability before the first network response, too.
updateControls();

</script></body></html>
)DRAGONWEB";
