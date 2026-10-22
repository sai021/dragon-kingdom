let collection=null,catalog=[],favorites=[],draft=null,reloading=false,previewMode='both';
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
const zoneCenters={1:[18,118],2:[302,118],3:[118,66],4:[202,66],5:[160,115],6:[160,228],7:[105,296],8:[65,153],9:[254,153]};
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
 const isAll=collection.active===0;$('#favorites').hidden=isAll;if($('#favorite-search')){$('#favorite-search').hidden=isAll;$('#favorite-search').value=''}
 $('#favorites').replaceChildren();for(const dragon of catalog){const row=document.createElement('div');row.className='check';row.dataset.name=dragon.name.toLowerCase();const input=document.createElement('input');input.type='checkbox';input.id='favorite-'+dragon.id;input.checked=favorites.includes(dragon.id);const label=document.createElement('label');label.htmlFor=input.id;label.textContent=dragon.name+(dragon.custom?(dragon.owned?' · made by you':' · custom dragon'):'');row.append(input,label);$('#favorites').append(row);input.onchange=()=>{if(input.checked){if(favorites.length>=12){input.checked=false;feedback('Choose up to 12 favourites.');return}favorites.push(dragon.id)}else favorites=favorites.filter(id=>id!==dragon.id);showFavoriteOrder()}}
 showFavoriteOrder();populateDragons();updateCreateButtonLabel();updateControls();
}
if($('#favorite-search'))$('#favorite-search').oninput=event=>{
 const q=event.target.value.trim().toLowerCase();
 for(const row of document.querySelectorAll('#favorites .check'))row.hidden=Boolean(q&&!row.dataset.name.includes(q));
};
for(const btn of document.querySelectorAll('.view-modes button'))btn.onclick=()=>{
 previewMode=btn.dataset.view;
 for(const b of document.querySelectorAll('.view-modes button'))b.setAttribute('aria-pressed',String(b===btn));
 drawDraft();
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
 return draft.originalColors?.[z]||draft.colors[z]||'#45415e';
}
function drawDraft(){
 if(!draft)return;const canvas=$('#preview'),ctx=canvas.getContext('2d'),selected=Number($('#region').value);
 ctx.fillStyle='#19182d';ctx.fillRect(0,0,320,320);
 if(previewMode!=='dragon'){
  for(let i=0;i<64;i++){
   const z=draft.zones[i],x=(i%8)*40,y=Math.floor(i/8)*40;
   ctx.fillStyle=(draft.colorMask&(1<<z))?draft.colors[z]:draft.originalPixels[i];
   ctx.fillRect(x+3,y+3,34,34);
   if(z===selected&&previewMode==='grid'){ctx.strokeStyle='#fff';ctx.lineWidth=2;ctx.strokeRect(x+3,y+3,34,34)}
  }
 }
 if(shapePaths&&previewMode!=='grid'){
  ctx.save();
  for(const z of drawOrder){
   const path=shapePaths[z];if(!path)continue;
   ctx.fillStyle=zoneDisplayColor(z);
   ctx.globalAlpha=previewMode==='both'?(z===selected?0.68:0.42):1;
   ctx.fill(path);
   ctx.globalAlpha=1;
   ctx.strokeStyle='#19182d';ctx.lineWidth=4.5;ctx.lineJoin='round';ctx.stroke(path);
   ctx.strokeStyle='rgba(255,249,239,0.55)';ctx.lineWidth=1.4;ctx.stroke(path);
  }
  if(shapePaths[selected]){
   if(previewMode==='both'){
    for(let i=0;i<64;i++)if(draft.zones[i]===selected){const x=(i%8)*40,y=Math.floor(i/8)*40;ctx.strokeStyle='rgba(255,255,255,0.65)';ctx.lineWidth=1.5;ctx.strokeRect(x+3,y+3,34,34)}
   }
   ctx.strokeStyle='#ffda8e';ctx.lineWidth=3.5;ctx.lineJoin='round';ctx.stroke(shapePaths[selected]);
  }
  ctx.font='14px system-ui,sans-serif';ctx.textAlign='center';ctx.textBaseline='middle';
  for(const z of drawOrder){
   const active=draft.effectZones.map((mask,i)=>mask&(1<<z)?i:null).filter(i=>i!==null);
   if(active.length===1&&zoneCenters[z]){const [cx,cy]=zoneCenters[z];ctx.fillText(effectIcons[active[0]],cx,cy)}
  }
  ctx.restore();
 }
}
function showRegion(){if(!draft)return;const z=Number($('#region').value);$('#region-color').value=draft.colors[z];const active=draft.effectZones.map((mask,i)=>mask&(1<<z)?i:null).filter(i=>i!==null);$('#region-effect').value=active.length===0?'none':active.length===1?String(active[0]):'keep';drawDraft()}
async function editDragon(id){
 if(commandBusy)return;if(draft&&!confirm('Discard your unsaved changes and start again?'))return;
 setCommandBusy(true);try{const detail=await request('/api/dragon-detail?id='+id),base=detail.id===detail.base?detail:await request('/api/dragon-detail?id='+detail.base);if(detail.profile!==base.profile||detail.generation!==base.generation)throw Error('Your collection changed. Reload the page before editing.');draft={...detail,originalPixels:base.pixels,originalColors:base.colors};$('#custom-name').value=detail.id===detail.base?'My '+detail.name:detail.name;$('#region').replaceChildren();for(let i=0;i<regionNames.length;i++){if(!detail.zones.includes(i))continue;const o=document.createElement('option');o.value=i;o.textContent=regionNames[i];$('#region').append(o)}$('#region').value=5;$('#copy-custom').hidden=$('#delete-custom').hidden=!detail.canEdit;$('#starting-dragon').replaceChildren();for(const d of catalog){const o=document.createElement('option');o.value=d.id;o.textContent=d.name;$('#starting-dragon').append(o)}$('#starting-dragon').value=detail.id;$('#editor').hidden=false;showRegion();$('#editor').scrollIntoView({behavior:'smooth',block:'start'});feedback('')}catch(e){feedback(e.message)}finally{setCommandBusy(false)}
};
$('#create-dragon').onclick=()=>editDragon($('#dragon').value===''?catalog[0].id:$('#dragon').value);
$('#starting-dragon').onchange=e=>editDragon(e.target.value);
$('#region').onchange=showRegion;
$('#preview').onclick=event=>{
 if(!draft)return;const canvas=event.currentTarget,bounds=canvas.getBoundingClientRect();
 const px=(event.clientX-bounds.left)/bounds.width*320,py=(event.clientY-bounds.top)/bounds.height*320;
 if(shapePaths&&previewMode!=='grid'){
  const ctx=canvas.getContext('2d');
  for(const z of hitOrder)if(shapePaths[z]&&draft.zones.includes(z)&&ctx.isPointInPath(shapePaths[z],px,py)){$('#region').value=z;showRegion();return}
 }
 const x=Math.min(7,Math.max(0,Math.floor(px/40))),y=Math.min(7,Math.max(0,Math.floor(py/40)));
 $('#region').value=draft.zones[y*8+x];showRegion();
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
