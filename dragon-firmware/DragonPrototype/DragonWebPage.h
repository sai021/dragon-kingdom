#pragma once
// Generated from web/dragon-kingdom.html by tools/embed_web.py.
const char page[] PROGMEM=R"DRAGONWEB(<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#19182d"><title>Dragon Kingdom</title>
<style>
*{box-sizing:border-box}body{font:18px system-ui,sans-serif;background:#19182d;color:#fff9ef;max-width:560px;margin:auto;padding:22px 18px 40px}h1{font-size:38px;color:#ffda8e;margin:8px 0}h2{font-size:24px;margin:0 0 16px}p{line-height:1.5}.eyebrow{color:#b6b4d2;font-size:14px;letter-spacing:2px;margin:0}section,details{background:#292740;padding:20px;border-radius:22px;margin:20px 0}button,input,select{font:inherit;min-height:52px;padding:13px;border-radius:14px;border:0;width:100%}input,select{background:#fff9ef;color:#19182d;margin:7px 0 16px}button{background:#c2edf0;color:#19182d;cursor:pointer;font-weight:650}button:disabled{opacity:.55;cursor:wait}button:focus-visible,input:focus-visible,select:focus-visible,summary:focus-visible{outline:3px solid #ffda8e;outline-offset:3px}.magic{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin:10px 0 16px}.magic button{min-height:88px}.magic span{display:block;font-size:28px;margin-bottom:4px}.fire{background:#ffd0a9}.glitter{background:#e1ceff}.magic button[aria-pressed=true]{box-shadow:inset 0 0 0 3px #ffda8e}.secondary{background:#45415e;color:#fff9ef;margin:12px 0}label{display:block}small{display:block;color:#cecbdf;font-size:14px;line-height:1.6}.status{font-size:15px;color:#d4f3ed;min-height:44px}.notice{background:#36314b;padding:14px;border-radius:14px;font-size:16px}summary{cursor:pointer;font-weight:650;min-height:32px}.parent{padding-top:20px}a{color:#c2edf0;overflow-wrap:anywhere}.check{display:flex;align-items:center;gap:10px;margin-bottom:18px}.check input{width:22px;min-height:22px;margin:0}.check label{font-size:15px}
</style></head><body>
<p class="eyebrow">YOUR LITTLE WORLD OF MAGIC</p><h1>Dragon Kingdom</h1>
<p id="status" class="status" role="status" aria-live="polite">Finding your dragon…</p>
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
<small>Your dragon adjusts its glow to the room and stays lit in daylight. Use Sleep to turn it off.</small><button id="create-dragon" class="secondary">Make a dragon</button></section>
<section id="editor" hidden><h2>Create your dragon</h2><small>Tap a part in the picture or choose it below. The picture shows the real 64 lights. Save to see it on your dragon.</small>
<canvas id="preview" width="320" height="320" style="width:100%;max-width:320px;display:block;margin:16px auto;touch-action:manipulation" aria-label="Eight by eight dragon colour preview"></canvas>
<label for="starting-dragon">Start from</label><select id="starting-dragon"></select><label for="custom-name">Dragon name</label><input id="custom-name" maxlength="32">
<label for="region">Dragon part</label><select id="region"></select>
<label for="region-color">Colour</label><input id="region-color" type="color" style="padding:5px">
<button id="reset-color" class="secondary">Use original colour for this part</button>
<label for="region-effect">Magic on this part</label><select id="region-effect"><option value="keep">Existing magic</option><option value="none">Still</option><option value="0">Rainbow</option><option value="1">Breathe</option><option value="2">Shimmer</option><option value="3">Glitter</option></select>
<button id="save-custom">Save my dragon</button><button id="copy-custom" class="secondary">Save a new copy</button><button id="cancel-custom" class="secondary">Cancel</button><button id="delete-custom" class="secondary" hidden>Delete this custom dragon</button>
</section>
<details id="profile-settings"><summary>My favourites &amp; starting glow</summary><div class="parent"><label for="profile-name">Profile name</label><input id="profile-name" maxlength="32"><label for="profile-glow">Starting glow</label><select id="profile-glow"></select><p id="favorites-help">Choose up to 12 favourites. Tapping your dragon cycles through them in the order you choose. The first is your starting dragon. Leave this empty to cycle through the whole collection.</p><p id="favorite-order" class="status"></p><div id="favorites" style="max-height:280px;overflow:auto"></div><button id="save-profile">Save profile</button><button id="delete-profile" class="secondary" hidden>Delete this profile</button><hr><label for="new-profile-name">New profile name</label><input id="new-profile-name" maxlength="32"><button id="new-profile">Add profile</button></div></details>
<details id="alarm"><summary>Sunrise alarm</summary><div class="parent">
<p>Wake up with your dragon. Its wings slowly glow from deep orange to warm sunrise light.</p>
<form id="alarm-form"><div class="check"><input id="alarm-enabled" type="checkbox"><label for="alarm-enabled">Wake me every day</label></div>
<label for="alarm-time">Wake-up time</label><input id="alarm-time" type="time" value="07:00" required>
<label for="alarm-duration">Sunrise length (minutes)</label><input id="alarm-duration" type="number" min="1" max="120" step="1" value="20" required>
<small>The sunrise starts this many minutes before your wake-up time. It works while the dragon is asleep and stays bright for 30 minutes afterwards, then returns to your previous lighting.</small>
<button id="save-alarm" style="margin-top:16px" disabled>Save alarm</button></form>
<p id="alarm-status" class="status" role="status" aria-live="polite">Loading alarm…</p>
<button id="preview-alarm" class="secondary">Try a 30-second sunrise</button><button id="stop-alarm" class="secondary" hidden>Stop sunrise</button>
<button id="sync-alarm" class="secondary">Set clock from my phone</button>
<small>Keep the dragon powered for its alarm. Saving uses your phone's time and daylight-saving rules. After a power cut, it needs internet time or this page opened again. A touch or play control stops the current sunrise.</small>
</div></details>
<details id="parents"><summary>For grown-ups · Wi-Fi &amp; help</summary><div class="parent">
<h2>Connect to home Wi-Fi</h2><p>Internet is optional. You can play while connected directly to your dragon.</p>
<button id="scan" type="button">Find my Wi-Fi</button><p id="scan-status" class="status" role="status"></p>
<form id="wifi"><label for="ssid">Home Wi-Fi name</label><input id="ssid" name="ssid" list="networks" maxlength="32" required autocomplete="off" autocapitalize="none" spellcheck="false"><datalist id="networks"></datalist>
<label for="wifi-password">Wi-Fi password</label><input id="wifi-password" name="password" type="password" maxlength="64" autocomplete="off" autocapitalize="none" spellcheck="false">
<div class="check"><input id="show-password" type="checkbox"><label for="show-password">Show password</label></div>
<button id="connect">Connect my dragon</button></form>
<small>Choose a 2.4 GHz network. If your Wi-Fi name doesn't appear, type it yourself. Leave the password blank only for an open network.</small>
<h2 style="margin-top:26px">Need to reconnect?</h2>
<small>Hold the dragon's touch pad while plugging it in. Keep holding through the blue startup pulses, then release when you see purple. Join the dragon network using your setup card and open <a href="http://192.168.4.1/">192.168.4.1</a>.<br><br>If your phone says the dragon network has no internet, choose to stay connected.</small>
<button id="forget" class="secondary">Forget home Wi-Fi</button><small>This keeps your dragon's setup-network password.</small>
</div></details>
<script>
const $=selector=>document.querySelector(selector),effects=['zones','breathe','colorcycle','glitter','incendio','leviosa'];
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
 document.body.setAttribute('aria-busy',String(commandBusy));$('#busy-status').hidden=!commandBusy;
}
function setCommandBusy(value){commandBusy=value;updateControls()}
async function loadAlarm(){
 alarmLoading=true;updateControls();
 try{renderAlarm(await request('/api/alarm'),true);renderAlarm(await request('/api/alarm/clock',phoneClock()));updateControls()}
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
 const controller=new AbortController(),timer=setTimeout(()=>controller.abort(),8000);
 try{const options={signal:controller.signal,cache:'no-store'};if(data){options.method='POST';options.headers={'X-Dragon-Request':'1'};options.body=new URLSearchParams(data)}const response=await fetch(path,options);if(!response.ok)throw Error(await response.text());return await response.json()}finally{clearTimeout(timer)}
}
function render(state){
 if(lastState&&state.profile!==undefined&&state.profile!==lastState.profile)reloadCollection();lastState=state;$('#status').textContent=state.connecting?'Connecting to home Wi-Fi…':state.connected?'Your dragon is on home Wi-Fi. Ready to play!':state.accessPoint?'Connected directly to your dragon. Ready to play!':'Home Wi-Fi is unavailable. Touch play still works.';
 if(document.activeElement!==$('#dragon')&&Array.from($('#dragon').options).some(option=>option.value===String(state.dragon)))$('#dragon').value=state.dragon;if(document.activeElement!==$('#brightness'))$('#brightness').value=state.brightness;
 const asleep=state.mode===9||state.brightness===0;$('#sleep').textContent=asleep?'Wake my dragon':'Put dragon to sleep';
 for(const button of document.querySelectorAll('[data-effect]'))button.setAttribute('aria-pressed',String(!asleep&&effects[state.mode]===button.dataset.effect));
 updateControls();
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
 try{render(await request('/api/state'));if(alarmFieldsLoaded)renderAlarm(await request('/api/alarm'));else await loadAlarm()}catch(error){$('#status').textContent='Connection lost. Rejoin the dragon network, or reconnect to home Wi-Fi.';try{const home=JSON.parse(sessionStorage.getItem('dragon-home'));if(home)showHomeAddress(home)}catch(e){}}finally{loading=false}
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
$('#forget').onclick=async()=>{if(commandBusy||!confirm('Forget home Wi-Fi? Your dragon will open its setup network. You will need to join it again using your setup card.'))return;setCommandBusy(true);try{await request('/api/forget-wifi',{});feedback('Home Wi-Fi forgotten. Join the dragon network using your setup card.');$('#home-address').hidden=true;try{sessionStorage.removeItem('dragon-home')}catch(e){}}catch(error){feedback(error.message)}finally{setCommandBusy(false)}};
async function initialize(){
 try{const dragons=await request('/api/dragons?catalog=1');await loadLibrary(dragons);$('#brightness').replaceChildren();for(let value=0;value<=100;value+=10){const option=document.createElement('option');option.value=value;option.textContent=value?value+'%':'Off';$('#brightness').append(option)}updateControls();await loadAlarm();await refresh()}catch(error){feedback('Could not load your dragons. Reconnect and refresh this page.')}
 clearTimeout(pollTimer);pollTimer=setTimeout(async function poll(){await refresh();if(!collection)await initialize();else pollTimer=setTimeout(poll,3000)},3000);
}
initialize();
</script>
<script>

let collection=null,catalog=[],favorites=[],draft=null,reloading=false;
function collectionRequest(path,data,context=collection){
 return request(path,{...data,profile:context.active??context.profile,generation:context.generation});
}
const regionNames=['Background','Left wing edge','Right wing edge','Left horn','Right horn','Face','Body','Tail','Left wing','Right wing'];
async function loadLibrary(dragons){
 catalog=dragons;collection=await request('/api/library');
 $('#profile').replaceChildren();for(const p of collection.profiles){const o=document.createElement('option');o.value=p.id;o.textContent=p.name;$('#profile').append(o)}$('#profile').value=collection.active;$('#profile').disabled=false;
 const p=collection.profiles.find(p=>p.id===collection.active);$('#profile-name').value=p.name;$('#profile-name').disabled=collection.active===0;$('#delete-profile').hidden=collection.active===0;$('#favorites-help').textContent=collection.active===0?'All contains every dragon and cannot be renamed or deleted.':'Choose up to 12 favourites. Your profile shows these plus your own creations. Tapping cycles through your collection. Uncheck and recheck to move a favourite to the end.';favorites=[...p.favorites];
 $('#profile-glow').replaceChildren();for(let n=10;n<=100;n+=10){const o=document.createElement('option');o.value=n;o.textContent=n+'%';$('#profile-glow').append(o)}$('#profile-glow').value=p.brightness;
 $('#favorites').hidden=collection.active===0;$('#favorites').replaceChildren();for(const dragon of catalog){const row=document.createElement('div');row.className='check';const input=document.createElement('input');input.type='checkbox';input.id='favorite-'+dragon.id;input.checked=favorites.includes(dragon.id);const label=document.createElement('label');label.htmlFor=input.id;label.textContent=dragon.name+(dragon.custom?(dragon.owned?' · made by you':' · custom dragon'):'');row.append(input,label);$('#favorites').append(row);input.onchange=()=>{if(input.checked){if(favorites.length>=12){input.checked=false;feedback('Choose up to 12 favourites.');return}favorites.push(dragon.id)}else favorites=favorites.filter(id=>id!==dragon.id);showFavoriteOrder()}}
 showFavoriteOrder();populateDragons();updateControls();
}
function visibleDragons(){if(collection.active===0)return catalog;const selected=collection.profiles.find(p=>p.id===collection.active).favorites.map(id=>catalog.find(d=>d.id===id)).filter(Boolean);return [...selected,...catalog.filter(d=>d.custom&&d.owned&&!selected.some(s=>s.id===d.id))]}
function populateDragons(){const dragons=visibleDragons();$('#dragon').replaceChildren();if(!dragons.length){const o=document.createElement('option');o.value='';o.textContent='Add favourites or make a dragon';$('#dragon').append(o)}for(const d of dragons){const o=document.createElement('option');o.value=d.id;o.textContent=d.name+(d.custom?' ✨':'');$('#dragon').append(o)}$('#dragon').disabled=!dragons.length;for(const button of document.querySelectorAll('[data-effect],#return,#sleep,#brightness'))button.disabled=!dragons.length;if(lastState&&dragons.some(d=>d.id===lastState.dragon))$('#dragon').value=lastState.dragon;else if(dragons.length)$('#dragon').value=dragons[0].id;updateControls()}
function showFavoriteOrder(){$('#favorite-order').textContent=collection.active===0?'All dragons':favorites.length?favorites.map((id,i)=>(i+1)+'. '+catalog.find(d=>d.id===id)?.name).join(' · '):'No favourites yet. Your own creations appear automatically.'}
async function reloadCollection(){if(reloading)return;reloading=true;try{await loadLibrary(await request('/api/dragons?catalog=1'))}catch(e){feedback(e.message)}finally{reloading=false}}
function closeEditor(){draft=null;$('#editor').hidden=true}
$('#profile').onchange=async event=>{
 const id=event.target.value;if(draft&&!confirm('Switch profiles and discard your unsaved dragon?')){event.target.value=collection.active;return}
 if(commandBusy){event.target.value=collection.active;return}setCommandBusy(true);try{await collectionRequest('/api/profile',{action:'select',id});closeEditor();lastState=null;await reloadCollection();render(await request('/api/state'));feedback('Profile selected.')}catch(e){event.target.value=collection.active;feedback(e.message)}finally{setCommandBusy(false)}
};
$('#save-profile').onclick=async()=>{if(commandBusy)return;setCommandBusy(true);try{await collectionRequest('/api/profile',{action:'update',name:$('#profile-name').value,brightness:$('#profile-glow').value,favorites:favorites.join(',')});await reloadCollection();render(await request('/api/state'));feedback('Profile saved.')}catch(e){feedback(e.message)}finally{setCommandBusy(false)}};
$('#new-profile').onclick=async()=>{if(commandBusy)return;if(draft&&!confirm('Create a profile and discard your unsaved dragon?'))return;setCommandBusy(true);try{await collectionRequest('/api/profile',{action:'create',name:$('#new-profile-name').value,brightness:100,favorites:''});closeEditor();lastState=null;await reloadCollection();render(await request('/api/state'));$('#new-profile-name').value='';feedback('Your new profile is ready.')}catch(e){feedback(e.message)}finally{setCommandBusy(false)}};
function drawDraft(){
 if(!draft)return;const canvas=$('#preview'),ctx=canvas.getContext('2d'),selected=Number($('#region').value);
 ctx.fillStyle='#19182d';ctx.fillRect(0,0,320,320);
 for(let i=0;i<64;i++){const z=draft.zones[i];ctx.fillStyle=(draft.colorMask&(1<<z))?draft.colors[z]:draft.originalPixels[i];const x=(i%8)*40,y=Math.floor(i/8)*40;ctx.fillRect(x+3,y+3,34,34);if(z===selected){ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.strokeRect(x+3,y+3,34,34)}}
}
function showRegion(){if(!draft)return;const z=Number($('#region').value);$('#region-color').value=draft.colors[z];const active=draft.effectZones.map((mask,i)=>mask&(1<<z)?i:null).filter(i=>i!==null);$('#region-effect').value=active.length===0?'none':active.length===1?String(active[0]):'keep';drawDraft()}
async function editDragon(id){
 if(commandBusy)return;if(draft&&!confirm('Discard your unsaved changes and start again?'))return;
 setCommandBusy(true);try{const detail=await request('/api/dragon-detail?id='+id),base=detail.id===detail.base?detail:await request('/api/dragon-detail?id='+detail.base);if(detail.profile!==base.profile||detail.generation!==base.generation)throw Error('Your collection changed. Reload the page before editing.');draft={...detail,originalPixels:base.pixels,originalColors:base.colors};$('#custom-name').value=detail.id===detail.base?'My '+detail.name:detail.name;$('#region').replaceChildren();for(let i=0;i<regionNames.length;i++){if(!detail.zones.includes(i))continue;const o=document.createElement('option');o.value=i;o.textContent=regionNames[i];$('#region').append(o)}$('#region').value=5;$('#copy-custom').hidden=$('#delete-custom').hidden=!detail.canEdit;$('#starting-dragon').replaceChildren();for(const d of catalog){const o=document.createElement('option');o.value=d.id;o.textContent=d.name;$('#starting-dragon').append(o)}$('#starting-dragon').value=detail.id;$('#editor').hidden=false;showRegion();$('#editor').scrollIntoView({behavior:'smooth',block:'start'});feedback('')}catch(e){feedback(e.message)}finally{setCommandBusy(false)}
};
$('#create-dragon').onclick=()=>editDragon($('#dragon').value===''?catalog[0].id:$('#dragon').value);
$('#starting-dragon').onchange=e=>editDragon(e.target.value);
$('#region').onchange=showRegion;
$('#preview').onclick=event=>{if(!draft)return;const bounds=event.currentTarget.getBoundingClientRect(),x=Math.min(7,Math.floor((event.clientX-bounds.left)/bounds.width*8)),y=Math.min(7,Math.floor((event.clientY-bounds.top)/bounds.height*8));$('#region').value=draft.zones[y*8+x];showRegion()};
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
