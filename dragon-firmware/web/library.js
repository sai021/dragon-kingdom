
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
