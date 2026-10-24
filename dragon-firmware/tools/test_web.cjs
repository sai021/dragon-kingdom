// Headless phone-size UI checks against simulated device responses.
// Usage: node tools/test_web.cjs PATH_TO_PLAYWRIGHT [PATH_TO_BROWSER]
const assert=require('node:assert/strict');
const fs=require('node:fs');
const path=require('node:path');
const {chromium}=require(process.argv[2]||'playwright');
const root=path.resolve(__dirname,'..');
const presets=JSON.parse(fs.readFileSync(path.join(root,'presets/dragons.json'),'utf8')).presets;
const zoneMap=[[8,1,1,8,9,2,2,9],[1,8,3,5,5,4,9,2],[1,8,5,5,5,5,9,2],[8,8,5,5,5,5,9,9],[8,8,8,6,6,9,9,9],[8,8,6,6,6,6,9,9],[8,7,6,6,6,6,9,9],[8,7,7,7,7,9,9,9]].flat();

(async()=>{
 const browser=await chromium.launch({headless:true,...(process.argv[3]?{executablePath:process.argv[3]}:{})});
 try{
  const page=await browser.newPage({viewport:{width:390,height:844},deviceScaleFactor:1,timezoneId:'Australia/Sydney'});
  const errors=[];page.on('pageerror',error=>errors.push(error.message));
  let state={firmware:'v0.3.0-beta.2',board:'s3',connected:false,accessPoint:true,connecting:false,mode:0,hostname:'Dragon-test',ip:'192.168.1.23',message:'Ready to play',dragon:0,brightness:100,profile:0};
  let board="s3";let updateMode="retry",chunks=[],starts=[],finishes=0,aborts=0,stateReads=0,checkIntents=[];
  let online={phase:0,busy:false,current:'v0.3.0-candidate',release:'',message:'Ready to check.',progress:0,channel:'release'};
  let profiles=[{id:0,name:"All",brightness:100,favorites:[]}],customs=[];
  let scanReads=0,scanWrites=0,forgot=false,generation=0,alarmGetFailures=0,heldPlay=null,playStarted=null;
  let alarm={enabled:false,minute:420,duration:20,clockReady:false,active:false,preview:false,progress:0},clockSyncs=0;
  await page.route('http://dragon.test/**',async route=>{
   const request=route.request(),url=new URL(request.url()),data=new URLSearchParams(request.postData()||'');
   const json=body=>route.fulfill({status:200,contentType:'application/json',body:JSON.stringify(body)});
   if(url.pathname==='/')return route.fulfill({contentType:'text/html',body:fs.readFileSync(path.join(root,'web/dragon-kingdom.html'),'utf8').replace('<script src="/library.js"></script>','<script>'+fs.readFileSync(path.join(root,'web/library.js'),'utf8')+'</script>')});
   if(url.pathname==='/api/parent/login')return data.get('password')==='dragon123'?json({token:'test-session'}):route.fulfill({status:401,body:'Parent password did not match.'});
   if(url.pathname==='/api/parent/logout')return json({});
   if(['/api/wifi','/api/scan','/api/forget-wifi','/api/backup','/api/restore','/api/reset','/api/update','/api/wifi/retry'].includes(url.pathname)&&request.headers()['x-dragon-parent']!=='test-session')return route.fulfill({status:401,body:'Unlock parent settings.'});
   if(url.pathname==='/api/support'){assert.equal(request.headers()['x-dragon-parent'],'test-session');return json({firmware:state.firmware,board})}
   if(url.pathname==='/api/update/start'){starts.push(Object.fromEntries(data));return json({})}
   if(url.pathname==='/api/update/chunk'){chunks.push(Object.fromEntries(data));if(updateMode==='cancel')await page.evaluate(()=>document.querySelector('#cancel-upload').click());if(updateMode==='retry'&&chunks.length===1)return route.fulfill({status:503,body:'Lost acknowledgement'});return json({offset:Number(data.get('offset'))+data.get('data').length/2})}
   if(url.pathname==='/api/update/finish'){finishes++;return json({})}
   if(url.pathname==='/api/update/abort'){aborts++;return json({})}
   if(url.pathname==='/api/update')return json({board,active:false,offset:0});
   if(url.pathname.startsWith('/api/update/online')){if(request.headers()['x-dragon-parent']!=='test-session')return route.fulfill({status:401,body:'Unlock parent settings.'});if(url.pathname.endsWith('/check')){checkIntents.push(data.get('intent'));assert(['release','beta'].includes(data.get('channel')));online={...online,channel:data.get('channel'),phase:2,busy:false,release:'v0.3.1',message:'Signed release v0.3.1 is available.'}};if(url.pathname.endsWith('/install')){assert.equal(data.get('release'),'v0.3.1');online={...online,phase:4,busy:true,message:'Downloading verified firmware.',progress:25}}if(url.pathname.endsWith('/cancel'))online={...online,phase:6,busy:false,message:'Online update cancelled. Existing firmware was kept.'};return json(online)}
   if(url.pathname==='/api/rotation')return json({enabled:0,shuffle:0,seconds:300});
   if(request.method()==='POST')assert.equal(request.headers()['x-dragon-request'],'1');
   if(request.method()==='POST'&&['/api/profile','/api/custom','/api/delete-profile','/api/delete-custom'].includes(url.pathname)){assert(data.has('profile')&&data.has('generation'));if(Number(data.get('profile'))!==state.profile||Number(data.get('generation'))!==generation)return route.fulfill({status:409,body:'Your collection changed. Reload the page before saving. Your changes have not been saved.'});generation++}
   if(url.pathname==='/api/alarm/clock'){
    assert(Number(data.get('epoch'))>1704067200);assert(Number(data.get('validUntil'))>Number(data.get('epoch')));
    assert(Number(data.get('count'))>=2&&Number(data.get('count'))<=4);clockSyncs++;alarm.clockReady=true;return json(alarm);
   }
   if(url.pathname==='/api/alarm'){
    if(request.method()==='GET'&&alarmGetFailures!==0){if(alarmGetFailures>0)alarmGetFailures--;return route.fulfill({status:503,body:'Temporary alarm failure'})}
    if(request.method()==='POST'){
     if(data.get('duration')==='13')return route.fulfill({status:500,body:'Alarm could not be saved. Try again.'});
     Object.assign(alarm,{enabled:data.get('enabled')==='1',minute:Number(data.get('minute')),duration:Number(data.get('duration'))});
    }return json(alarm);
   }
   if(url.pathname==='/api/alarm/preview'){Object.assign(alarm,{active:true,preview:true,progress:1});return json(alarm)}
   if(url.pathname==='/api/alarm/stop'){Object.assign(alarm,{active:false,preview:false,progress:0});return json(alarm)}
   if(url.pathname==='/api/dragons')return json([{id:0,name:'Blue'},{id:1,name:'Sundew'},...customs.map(d=>({...d,owned:d.owner===state.profile}))]);
   if(url.pathname==='/api/library')return json({active:state.profile,generation,profiles:profiles.filter(Boolean),customLimit:8});
   if(url.pathname==='/api/dragon-detail'){const id=Number(url.searchParams.get('id')),custom=customs.find(d=>d.id===id);return json({profile:state.profile,generation,id,base:custom?.base??id,name:custom?.name??'Blue',canEdit:Boolean(custom&&custom.owner===state.profile),colorMask:custom?.colorMask??0,colors:custom?.colors??Array(10).fill('#123456'),pixels:presets[custom?.base??id].pixels,zones:zoneMap,effectZones:custom?.effectZones??[0,0,0,0]})}
   if(url.pathname==='/api/custom'){const id=Number(data.get('id'))<0?81+customs.length:Number(data.get('id'));const custom={id,owner:state.profile,custom:true,name:data.get('name'),base:Number(data.get('base')),colorMask:Number(data.get('colorMask')),colors:data.get('colors').match(/.{6}/g).map(c=>'#'+c),effectZones:data.get('effectZones').split(',').map(Number)};customs=customs.filter(d=>d.id!==id);customs.push(custom);state.dragon=id;state.mode=0;return json({id})}
   if(url.pathname==='/api/delete-profile'){const id=Number(data.get('id'));assert.notEqual(id,0);for(const custom of customs)if(custom.owner===id)custom.owner=0;profiles[id]=null;state.profile=0;state.dragon=0;return json({})}
   if(url.pathname==='/api/delete-custom'){const id=Number(data.get('id'));customs=customs.filter(d=>d.id!==id);for(const p of profiles)if(p)p.favorites=p.favorites.filter(value=>value!==id);if(state.dragon===id)state.dragon=0;return json({})}
   if(url.pathname==='/api/profile'){const action=data.get('action');if(action==='create'){state.profile=profiles.length;profiles.push({id:state.profile,name:data.get('name'),brightness:100,favorites:[]})}else if(action==='select')state.profile=Number(data.get('id'));else{Object.assign(profiles[state.profile],{name:data.get('name'),brightness:Number(data.get('brightness')),favorites:data.get('favorites')?data.get('favorites').split(',').map(Number):[]})}state.dragon=profiles[state.profile].favorites[0]??0;state.brightness=profiles[state.profile].brightness;state.mode=0;return json({})}
   if(url.pathname==='/api/state'){stateReads++;return json(state)}
   if(url.pathname==='/api/play'){
    if(heldPlay){playStarted();await heldPlay}
    if(data.get('action')==='dragon'){state.dragon=Number(data.get('value'));state.mode=0}
    if(data.get('action')==='effect')state.mode=['zones','breathe','colorcycle','glitter','incendio','leviosa'].indexOf(data.get('value'));
    if(data.get('action')==='toggle'){state.mode=state.mode===9?0:9}
    if(data.get('action')==='brightness')state.brightness=Number(data.get('value'));
    return json({});
   }
   if(url.pathname==='/api/scan'){
    if(request.method()==='POST'){scanWrites++;return json({})}
    scanReads++;return json({scanning:scanReads===1,networks:scanReads===1?[]:[{name:'Family Wi-Fi',open:false}]});
   }
   if(url.pathname==='/api/wifi'){
    if(data.get('password')==='wrong-pass'){state.message='Could not join home Wi-Fi. Check the name and password, then try again.';return json({})}
    assert.equal(data.get('ssid'),'Family Wi-Fi');state.connected=true;state.message='Home Wi-Fi saved';return json({});
   }
   if(url.pathname==='/api/forget-wifi'){forgot=true;state.connected=false;return json({})}
   return route.fulfill({status:404,body:'Missing mock endpoint'});
  });
  await page.goto('http://dragon.test/');
  await page.locator('#dragon:not([disabled])').waitFor();await page.waitForFunction(()=>document.querySelector('#device-firmware').textContent.includes('v0.3.0-beta.2'));assert.match(await page.textContent('#device-firmware'),/v0\.3\.0-beta\.2.*ESP32-S3/);assert.equal(await page.isVisible('#device-firmware'),true);assert.equal(await page.isVisible('#parent-controls'),false);state.board='c3';await page.evaluate(()=>refresh());assert.match(await page.textContent('#device-firmware'),/ESP32-C3/);state.board='s3';await page.evaluate(()=>refresh());
  await page.locator('#save-alarm:not([disabled])').waitFor({state:'attached'});assert.equal(clockSyncs,1);
  await page.click('#alarm summary');await page.check('#alarm-enabled');await page.fill('#alarm-time','06:30');await page.fill('#alarm-duration','30');await page.click('#save-alarm');
  await page.waitForFunction(()=>document.querySelector('#alarm-status').textContent.startsWith('Daily sunrise saved'));
  assert.equal(alarm.minute,390);assert.equal(alarm.duration,30);assert.equal(alarm.enabled,true);
  await page.fill('#alarm-time','08:15');await page.evaluate(()=>refresh());assert.equal(await page.inputValue('#alarm-time'),'08:15'); // polling preserves drafts
  await page.reload();await page.locator('#save-alarm:not([disabled])').waitFor({state:'attached'});await page.click('#alarm summary');assert.equal(await page.inputValue('#alarm-time'),'06:30');
  await page.fill('#alarm-duration','13');await page.click('#save-alarm');await page.getByText('Alarm could not be saved. Try again.',{exact:true}).waitFor();assert.equal(alarm.duration,30);
  await page.fill('#alarm-duration','30');await page.click('#preview-alarm');await page.locator('#stop-alarm:not([hidden])').waitFor();assert.equal(alarm.preview,true);
  await page.click('#stop-alarm');await page.locator('#stop-alarm[hidden]').waitFor({state:'attached'});assert.equal(alarm.active,false);
  await page.uncheck('#alarm-enabled');await page.click('#save-alarm');await page.waitForFunction(()=>document.querySelector('#alarm-status').textContent.startsWith('Daily alarm is off'));assert.equal(alarm.enabled,false);
  await page.locator('#alarm').screenshot({path:path.join(root,'.tools/sunrise-alarm-phone.png')});await page.click('#alarm summary');
  await page.selectOption('#dragon','1');
  await page.waitForFunction(()=>document.querySelector('#dragon').value==='1');
  await page.click('[data-effect="glitter"]');
  await page.locator('[data-effect="glitter"][aria-pressed="true"]').waitFor();
  await page.click('[data-effect="incendio"]');
  await page.locator('[data-effect="incendio"][aria-pressed="true"]').waitFor();
  await page.click('#sleep');await page.getByRole('button',{name:'Wake my dragon',exact:true}).waitFor();
  await page.click('#sleep');await page.getByRole('button',{name:'Put dragon to sleep',exact:true}).waitFor();
  await page.click('#profile-settings summary');assert.equal(await page.locator('#delete-profile').isVisible(),false);await page.fill('#new-profile-name','Test');await page.click('#new-profile');await page.waitForFunction(()=>document.querySelector('#feedback').textContent==='Your new profile is ready.');assert.equal(await page.locator('#dragon').isDisabled(),true);
  // Filtering must hide rendered rows and retain hidden selections.
  await page.fill('#favorite-search','blue');
  assert.equal(await page.locator('#favorites .check:visible').count(),1);
  await page.check('#favorite-0');await page.fill('#favorite-search','sundew');
  assert.equal(await page.locator('#favorites .check:visible').count(),1);
  assert.equal(await page.locator('#favorite-0').isVisible(),false);
  assert.equal(await page.locator('#favorite-0').isChecked(),true);
  await page.fill('#favorite-search','no matching dragon');
  assert.equal(await page.locator('#favorites .check:visible').count(),0);
  assert.equal(await page.locator('#favorite-search-status').textContent(),'No dragons match your search.');
  await page.fill('#favorite-search','');await page.uncheck('#favorite-0');
  assert.equal(await page.locator('#favorites .check:visible').count(),2);
  await page.click('#create-dragon');await page.locator('#editor:not([hidden])').waitFor();
  await page.waitForFunction(()=>draft!==null&&!commandBusy);
  assert.equal(await page.locator('[data-view]').count(),0);
  // Every illustrated part is selectable at phone scale; background taps do
  // not select invisible LED cells. Selection preserves original markings.
  const originalPixels=await page.evaluate(()=>[...draft.originalPixels]);
  for(const zone of [1,2,3,4,5,6,7,8,9]){
   await page.locator('#preview').evaluate((canvas,z)=>{const b=canvas.getBoundingClientRect(),[x,y]=zoneCenters[z];canvas.dispatchEvent(new MouseEvent('click',{bubbles:true,clientX:b.left+x*b.width/320,clientY:b.top+y*b.height/320}))},zone);
   assert.equal(await page.inputValue('#region'),String(zone));
  }
  await page.locator('#preview').evaluate(canvas=>{const b=canvas.getBoundingClientRect();canvas.dispatchEvent(new MouseEvent('click',{bubbles:true,clientX:b.left+1,clientY:b.top+1}))});
  assert.equal(await page.inputValue('#region'),'9');
  assert.equal(await page.evaluate(()=>draft.colorMask),0);
  assert.deepEqual(await page.evaluate(()=>draft.originalPixels),originalPixels);
  await page.fill('#custom-name','My Spark');await page.selectOption('#region','5');
  await page.locator('#region-color').evaluate(input=>{input.value='#ff6600';input.dispatchEvent(new Event('input',{bubbles:true}))});
  await page.selectOption('#region-effect','3');
  await page.locator('#editor').screenshot({path:path.join(root,'.tools/custom-editor-phone.png')});
  await page.click('#save-custom');await page.waitForFunction(()=>document.querySelector('#feedback').textContent==='Your dragon is saved!');
  assert.equal(customs[0].name,'My Spark');assert.equal(customs[0].colorMask,1<<5);assert.equal(customs[0].effectZones[3],1<<5);
  // The save response renders while controls are disabled. Immediate editing
  // must follow the newly saved selection, without waiting for a polling tick.
  await page.evaluate(()=>clearInterval(pollTimer));
  assert.equal(await page.inputValue('#dragon'),'81');
  assert.equal(await page.locator('#create-dragon').textContent(),'Edit or copy custom dragon');
  await page.click('#create-dragon');await page.waitForFunction(()=>!commandBusy&&draft?.id===81);
  await page.fill('#custom-name','My Spark copy');await page.click('#copy-custom');await page.waitForFunction(()=>!commandBusy&&draft===null);
  assert.equal(await page.inputValue('#dragon'),'82');
  await page.click('#create-dragon');await page.waitForFunction(()=>!commandBusy&&draft?.id===82);
  assert.equal(await page.inputValue('#custom-name'),'My Spark copy');
  page.once('dialog',dialog=>dialog.accept());await page.click('#delete-custom');await page.waitForFunction(()=>!commandBusy&&draft===null);
  assert.equal(customs.length,1);assert.equal(customs[0].id,81);assert.equal(customs[0].name,'My Spark');
  await page.check('#favorite-81');await page.selectOption('#profile-glow','40');await page.click('#save-profile');
  await page.waitForFunction(()=>document.querySelector('#feedback').textContent==='Profile saved.');assert.deepEqual(profiles[1].favorites,[81]);assert.equal(state.brightness,40);assert.equal(await page.locator('#dragon option').count(),1);assert.equal(await page.locator('#dragon option[value="0"]').count(),0);
  await page.fill('#new-profile-name','Alex');await page.click('#new-profile');await page.waitForFunction(()=>document.querySelector('#feedback').textContent==='Your new profile is ready.');
  assert.equal(state.profile,2);assert.equal(await page.locator('#dragon option[value="81"]').count(),0);
  await page.selectOption('#profile','1');await page.waitForFunction(()=>document.querySelector('#feedback').textContent==='Profile selected.');
  assert.equal(await page.locator('#dragon option[value="81"]').count(),1);
  await page.reload();await page.locator('#profile:not([disabled])').waitFor();assert.equal(await page.inputValue('#profile'),'1');
  assert.equal(await page.locator('#dragon option[value="81"]').count(),1);
  await page.click('#profile-settings summary');page.once('dialog',dialog=>dialog.accept());await page.click('#delete-profile');await page.waitForFunction(()=>document.querySelector('#feedback').textContent==='Profile deleted. Its creations are in All.');assert.equal(state.profile,0);assert.equal(customs[0].owner,0);assert.equal(await page.locator('#dragon option').count(),3);assert.equal(await page.locator('#delete-profile').isVisible(),false);assert.equal(await page.locator('#dragon option[value="81"]').count(),1);
  await page.selectOption('#dragon','81');await page.click('#create-dragon');await page.locator('#editor:not([hidden])').waitFor();page.once('dialog',dialog=>dialog.accept());await page.click('#delete-custom');await page.waitForFunction(()=>document.querySelector('#feedback').textContent==='Custom dragon deleted.');assert.equal(customs.length,0);assert.deepEqual(profiles[0].favorites,[]);
  await page.click('#parents summary');assert.equal(await page.isVisible('#parent-controls'),false);assert.equal(await page.isVisible('#scan'),false);await page.fill('#parent-password','wrong-password');await page.locator('#parent-login button').click();await page.waitForFunction(()=>document.querySelector('#parent-status').textContent==='Parent password did not match.');assert.equal(await page.isVisible('#parent-controls'),false);
  await page.fill('#parent-password','dragon123');await page.locator('#parent-login button').click();await page.waitForFunction(()=>document.querySelector('#parent-status').textContent.includes('unlocked'));await page.waitForFunction(()=>document.querySelector('#update-board').textContent.includes('ESP32-S3'));assert.match(await page.textContent('#update-board'),/dragon-s3\.dragon\.json/);assert.equal(await page.inputValue('#parent-password'),'');assert.equal(await page.isVisible('#parent-controls'),true);assert.equal(await page.locator('#parent-setup').count(),0);assert.equal(await page.isDisabled('#online-check'),true);assert.equal(await page.isVisible('#setup-internet-warning'),true);assert.equal(await page.inputValue('#update-channel'),'release');await page.selectOption('#update-channel','beta');assert.equal(await page.isVisible('#beta-warning'),true);state.connected=true;state.accessPoint=false;await page.evaluate(()=>refresh());assert.equal(await page.isDisabled('#online-check'),false);await page.click('#online-check');await page.locator('#online-install:not([hidden])').waitFor();page.once('dialog',dialog=>dialog.accept());await page.click('#online-install');await page.waitForFunction(()=>document.querySelector('#online-status').textContent.includes('25%'));assert.equal(await page.isDisabled('#update'),true);await page.click('#online-cancel');await page.waitForFunction(()=>document.querySelector('#online-status').textContent.includes('cancelled'));await page.click('#parent-lock');await page.waitForFunction(()=>document.querySelector('#parent-controls').hidden);assert.equal(await page.isVisible('#parent-controls'),false);assert.equal(await page.inputValue('#update-channel'),'release');board='c3';await page.fill('#parent-password','dragon123');await page.locator('#parent-login button').click();await page.waitForFunction(()=>!document.querySelector('#parent-controls').hidden);await page.waitForFunction(()=>document.querySelector('#update-board').textContent.includes('ESP32-C3'));assert.match(await page.textContent('#update-board'),/dragon-c3\.dragon\.json/);await page.evaluate(async()=>{parentExpiry=Date.now()-1;await request('/api/state')});assert.equal(await page.isVisible('#parent-controls'),false);await page.fill('#parent-password','dragon123');await page.locator('#parent-login button').click();await page.waitForFunction(()=>!document.querySelector('#parent-controls').hidden);state.connected=false;state.accessPoint=true;await page.evaluate(()=>refresh());assert.equal(await page.isDisabled('#online-check'),true);await page.click('#scan');
  await page.waitForFunction(()=>document.querySelector('#networks').children.length===1);
  assert.equal(scanWrites,1);assert.equal(scanReads,2);
  await page.fill('#ssid','Family Wi-Fi');await page.fill('#wifi-password','wrong-pass');
  await page.check('#show-password');assert.equal(await page.getAttribute('#wifi-password','type'),'text');
  await page.click('#connect');await page.locator('#connect-status').filter({hasText:'Could not join home Wi-Fi.'}).waitFor();
  await page.fill('#wifi-password','correct-pass');await page.click('#connect');
  await page.locator('#home-address:not([hidden])').waitFor();
  assert.equal(await page.locator('#home-address a').first().getAttribute('href'),'http://Dragon-test.local/');
  await page.waitForFunction(()=>document.querySelector('#wifi-password').value==='');assert.equal(await page.inputValue('#wifi-password'),'');
  assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth),true);
  await page.screenshot({path:path.join(root,'.tools/online-parent-phone.png'),fullPage:true});
  await page.locator('#parents').evaluate(element=>element.open=false);
  await page.screenshot({path:path.join(root,'.tools/web-preview-phone.png'),fullPage:true});
  await page.locator('#parents').evaluate(element=>element.open=true);
  page.once('dialog',dialog=>dialog.accept());await page.click('#forget');
  await page.waitForFunction(()=>document.querySelector('#feedback').textContent.startsWith('Home Wi-Fi forgotten'));
  assert.equal(forgot,true);
  // An empty saved profile must stay unavailable on a full page reload.
  state.profile=2;generation++;
  await page.reload();await page.waitForFunction(()=>collection?.active===2&&document.querySelector('#brightness').options.length===11);
  assert.equal(await page.locator('#dragon').isDisabled(),true);assert.equal(await page.locator('#brightness').isDisabled(),true);
  // A transient initial alarm failure retries; clock sync can also safely hydrate the form.
  Object.assign(alarm,{enabled:true,minute:365,duration:35});alarmGetFailures=-1;
  await page.reload();await page.waitForFunction(()=>collection!==null&&!loading&&document.querySelector('#alarm-status').textContent.startsWith('Could not load'));
  assert.equal(await page.locator('#save-alarm').isDisabled(),true);
  alarmGetFailures=0;await page.evaluate(()=>refresh());await page.waitForFunction(()=>alarmFieldsLoaded);
  assert.equal(await page.inputValue('#alarm-time'),'06:05');assert.equal(await page.inputValue('#alarm-duration'),'35');assert.equal(await page.isChecked('#alarm-enabled'),true);
  alarmGetFailures=-1;await page.reload();await page.waitForFunction(()=>collection!==null&&!loading&&document.querySelector('#alarm-status').textContent.startsWith('Could not load'));
  await page.click('#alarm summary');await page.click('#sync-alarm');await page.waitForFunction(()=>!commandBusy&&alarmFieldsLoaded);
  assert.equal(await page.inputValue('#alarm-time'),'06:05');assert.equal(await page.inputValue('#alarm-duration'),'35');assert.equal(await page.isChecked('#alarm-enabled'),true);
  alarmGetFailures=0;
  // A pending play request visibly disables conflicting controls; a synthetic
  // onchange is also rejected without leaving a misleading selected profile.
  state.profile=0;generation++;await page.reload();await page.waitForFunction(()=>collection?.active===0&&alarmFieldsLoaded);
  let releasePlay;heldPlay=new Promise(resolve=>releasePlay=resolve);const started=new Promise(resolve=>playStarted=resolve);
  await page.click('[data-effect="glitter"]');await started;
  assert.equal(await page.locator('#profile').isDisabled(),true);assert.equal(await page.locator('#busy-status').isVisible(),true);
  await page.evaluate(()=>{const node=document.querySelector('#profile');node.value='2';node.dispatchEvent(new Event('change',{bubbles:true}))});
  assert.equal(await page.inputValue('#profile'),'0');assert.equal(state.profile,0);
  heldPlay=null;releasePlay();await page.waitForFunction(()=>!commandBusy);
  assert.equal(await page.locator('#profile').isDisabled(),false);
  // A changed collection rejects a stale creation save and preserves its draft.
  await page.click('#create-dragon');await page.locator('#editor:not([hidden])').waitFor();await page.fill('#custom-name','Unsaved draft');generation++;
  await page.click('#save-custom');await page.getByText('Your collection changed.',{exact:false}).waitFor();
  assert.equal(await page.inputValue('#custom-name'),'Unsaved draft');assert.equal(await page.locator('#editor').isVisible(),true);assert.equal(customs.length,0);
  // Shipping controls: visibility suppression, explicit intent, retry identity and cancellation.
  await page.reload();await page.waitForFunction(()=>collection!==null&&!loading);
  await page.evaluate(()=>{clearTimeout(pollTimer);Object.defineProperty(document,'hidden',{configurable:true,get:()=>true})});
  const readsBefore=stateReads;await page.evaluate(()=>refresh());assert.equal(stateReads,readsBefore);
  await page.evaluate(()=>{Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});document.dispatchEvent(new Event('visibilitychange'))});
  await page.waitForFunction(()=>!loading);assert(stateReads>readsBefore);
  await page.click('#parents summary');await page.fill('#parent-password','dragon123');await page.locator('#parent-login button').click();await page.waitForFunction(()=>parentToken&&!loading);
  state.connected=true;state.accessPoint=false;await page.evaluate(()=>refresh());
  await page.click('#online-check');await page.locator('#online-install:not([hidden])').waitFor();assert.equal(checkIntents.at(-1),'upgrade');
  await page.check('#return-release');assert.equal(await page.isVisible('#online-install'),false);
  await page.click('#online-check');await page.locator('#online-install:not([hidden])').waitFor();assert.equal(checkIntents.at(-1),'return-release');
  // Native-sized checkboxes and parent action spacing at phone width.
  for(const id of ['return-release','rotate-enabled']){const box=await page.locator('#'+id).evaluate(el=>{const r=el.getBoundingClientRect(),c=getComputedStyle(el);return {width:parseFloat(c.width),height:parseFloat(c.height)}});assert.equal(box.width,22);assert.equal(box.height,22)}
  await page.evaluate(()=>{lastState.accessPoint=false;render(lastState)});assert.match(await page.textContent('#connect-status'),/Connected to home Wi-Fi/);assert.doesNotMatch(await page.textContent('#connect-status'),/closes shortly/);
  await page.evaluate(()=>{lastState.accessPoint=true;render(lastState)});assert.match(await page.textContent('#connect-status'),/closes shortly/);await page.evaluate(()=>{lastState.accessPoint=false;render(lastState)});
  assert.match(await page.textContent('#offline-update-help'),/stay here/);
  const spacing=await page.evaluate(()=>{const rect=id=>document.querySelector(id).getBoundingClientRect();return rect('#backup').top-rect('#support-details').bottom});assert(spacing>=12);
  const downloadPromise=page.waitForEvent('download');await page.click('#support-details');const download=await downloadPromise;
  assert.equal(download.suggestedFilename(),'dragon-support.json');assert.deepEqual(JSON.parse(fs.readFileSync(await download.path(),'utf8')),{firmware:state.firmware,board});
  const pkg={format:2,board,tag:'v0.3.0',capabilities:1,schema:1,size:600,image:'ab'.repeat(600),sha256:'0'.repeat(64),signature:'0'.repeat(512)};
  await page.setInputFiles('#update-file',{name:'test.dragon.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(pkg))});
  await page.click('#update');await page.waitForFunction(()=>!commandBusy&&document.querySelector('#update-status').textContent.startsWith('Verified.'));
  assert.equal(finishes,1);assert.equal(starts.at(-1).intent,'return-release');assert.deepEqual(chunks[0],chunks[1]);assert.equal(chunks.length,3);
  await page.fill('#parent-password','dragon123');await page.locator('#parent-login button').click();await page.waitForFunction(()=>parentToken&&!loading);
  updateMode='cancel';chunks=[];pkg.size=20;pkg.image='ab'.repeat(20);
  await page.setInputFiles('#update-file',{name:'test.dragon.json',mimeType:'application/json',buffer:Buffer.from(JSON.stringify(pkg))});
  await page.click('#update');await page.waitForFunction(()=>!commandBusy&&document.querySelector('#update-status').textContent.startsWith('Upload cancelled.'));
  assert.equal(finishes,1);assert.equal(aborts,1);assert.equal(chunks.length,1);
  assert.deepEqual(errors,[]);
  console.log('PASS: shipping upload retry/cancel, return intent, support download, hidden polling; initial alarm failure recovery, safe clock-sync hydration, busy controls, empty-profile reload and stale-draft preservation; daily sunrise save/reload, DST clock payloads, preview/stop, save failure and draft preservation; phone layout, play/effects, Wi-Fi setup, custom editing and profiles.');
 }finally{await browser.close()}
})().catch(error=>{console.error(error);process.exitCode=1});
