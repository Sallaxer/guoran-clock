const $=s=>document.querySelector(s);
const icons={sun:'<circle cx="12" cy="12" r="4"/><path d="M12 2v2m0 16v2M2 12h2m16 0h2M5 5l1.5 1.5m11 11L19 19M5 19l1.5-1.5m11-11L19 5"/>',clock:'<circle cx="12" cy="12" r="9"/><path d="M12 6v6l4 2"/>',sliders:'<path d="M4 6h16M4 12h16M4 18h16"/><circle cx="8" cy="6" r="2" fill="currentColor"/><circle cx="16" cy="12" r="2" fill="currentColor"/><circle cx="10" cy="18" r="2" fill="currentColor"/>',book:'<path d="M3 4h7l2 2 2-2h7v16h-7l-2 2-2-2H3zM12 6v16"/>',terminal:'<rect x="3" y="4" width="18" height="16" rx="3"/><path d="m7 9 3 3-3 3m6 0h4"/>',bluetooth:'<path d="m7 7 10 10-5 5V2l5 5L7 17"/>',info:'<circle cx="12" cy="12" r="9"/><path d="M12 11v6m0-10v1"/>',refresh:'<path d="M20 7v5h-5M4 17v-5h5M5 8a7.5 7.5 0 0 1 13-3l2 3M4 16l2 3a7.5 7.5 0 0 0 13-3"/>',palette:'<path d="M12 3a9 9 0 1 0 0 18c3 0 1-4 3-4h3c4-1 4-7 1-10a10 10 0 0 0-7-4z"/><circle cx="7" cy="10" r="1"/><circle cx="10" cy="6" r="1"/><circle cx="15" cy="7" r="1"/>',remote:'<rect x="7" y="2" width="10" height="20" rx="4"/><circle cx="12" cy="7" r="1.5"/><path d="M10 12h4m-4 4h4"/>',power:'<path d="M12 3v9m-6-6a8 8 0 1 0 12 0"/>',back:'<path d="m8 5-5 5 5 5M3 10h11a5 5 0 0 1 0 10h-2"/>',download:'<path d="M12 3v12m-5-5 5 5 5-5M4 16v5h16v-5"/>',search:'<circle cx="10" cy="10" r="7"/><path d="m15 15 6 6"/>',tube:'<rect x="5" y="2" width="14" height="20" rx="6"/><path d="M9 6h6v12H9zM8 20h8"/>'};
function icon(name){return `<svg viewBox="0 0 24 24" aria-hidden="true">${icons[name]||icons.info}</svg>`}
let state={connected:false,busy:false,snapshot:null,requested:{},schedule:{on:'',off:''},devices:[],logs:[],theme:'light',language:'ru'},selectedDevice=null,currentPage='home';
let draftColor='#ff9500',draftDirty=false,apiReady=false,localBusy=false,pollRunning=false,connectingAttempt=false,toastTimer;
let scheduleEditing=false,scheduleSave=Promise.resolve();
const presets=[['#ff9500','amber'],['#ffd49b','warm'],['#ec6451','coral'],['#b47dd0','lavender'],['#729dda','sky'],['#69c8c8','teal'],['#94ba73','sage'],['#ffffff','white']];
const featureKeys=['A','C','F','B','D','E'];
function toggle(key,label){return `<button data-switch="${key}" class="toggle unknown" role="switch" aria-checked="false" data-device data-i18n-aria="${label}"><i></i></button>`}
$('#settings-grid').innerHTML=featureKeys.map(key=>`<article class="card setting-card"><div class="row"><h2 data-i18n="feature${key}"></h2>${toggle(key,'feature'+key)}</div><p data-i18n="desc${key}"></p><div class="setting-state" data-setting-state="${key}"></div></article>`).join('');
$('#channels').innerHTML=Array.from({length:6},(_,i)=>`<button class="channel unknown" data-switch="${i+1}" role="switch" aria-checked="false" data-device>${icon('tube')}<span></span><small></small></button>`).join('');
$('#alarm-rows').innerHTML=['alarm1','alarm2'].map((kind,i)=>`<div class="time-row"><div><strong data-i18n="${kind}"></strong><div class="time-input-row"><input type="time" data-time="${kind}" data-device data-i18n-aria="${kind}"><button class="secondary" data-save-time="${kind}" data-device data-i18n="set"></button></div><span class="time-warning" data-time-warning="${kind}"></span></div>${toggle(String(8+i),kind)}</div>`).join('');
$('#presets').innerHTML=presets.map(([color,name])=>`<button class="preset" style="background:${color}" data-color="${color}" data-i18n-title="${name}" data-i18n-aria="${name}" data-device></button>`).join('');
document.querySelectorAll('[data-icon]').forEach(el=>el.innerHTML=icon(el.dataset.icon));
function applyLanguage(value){
  language=value;document.documentElement.lang=value;$('#language').value=value;
  document.querySelectorAll('[data-i18n]').forEach(el=>el.textContent=t(el.dataset.i18n));
  document.querySelectorAll('[data-i18n-aria]').forEach(el=>el.setAttribute('aria-label',t(el.dataset.i18nAria)));
  document.querySelectorAll('[data-i18n-title]').forEach(el=>el.title=t(el.dataset.i18nTitle));
  document.querySelectorAll('.channel').forEach(el=>{const label=t('channel',{n:el.dataset.switch});el.querySelector('span').textContent=label;el.setAttribute('aria-label',label)});
  $('#remote-menu-table').innerHTML=$('#menu-table').innerHTML=menuRows.map(([code,name,values])=>`<tr><td>${code}</td><td>${name[value==='en'?1:0]}</td><td>${values[value==='en'?1:0]}</td></tr>`).join('');
  $('#page-title').textContent=t(currentPage);clockTick();applyTheme(state.theme);drawState();renderDevices();
}
function showPage(name){currentPage=name;document.querySelectorAll('.page').forEach(el=>el.classList.toggle('active',el.id==='page-'+name));document.querySelectorAll('[data-page]').forEach(el=>el.classList.toggle('active',el.dataset.page===name));$('#page-title').textContent=t(name);window.scrollTo(0,0)}
document.querySelectorAll('[data-page]').forEach(el=>el.onclick=()=>showPage(el.dataset.page));$('.brand').onclick=e=>{e.preventDefault();showPage('home')};
$('#protection-help').onclick=()=>{showPage('guide');$('#guide-protection').scrollIntoView({block:'start',behavior:'smooth'})};
function toast(text,error=false){clearTimeout(toastTimer);$('#toast').textContent=text;$('#toast').classList.toggle('error',error);$('#toast').classList.add('show');toastTimer=setTimeout(()=>$('#toast').classList.remove('show'),4500)}
function updateDisabled(){
  const disabled=!apiReady||!state.connected||state.busy||localBusy;
  document.querySelectorAll('[data-device]').forEach(el=>el.disabled=disabled);
  for(const id of ['scan','enable-bt'])$('#'+id).disabled=!apiReady||state.busy||localBusy;
  $('#connect').disabled=!apiReady||!selectedDevice||state.busy||localBusy;
  $('#disconnect').disabled=!apiReady||!state.connected||state.busy||localBusy;
  $('#schedule-apply').disabled=disabled||!effectiveSwitch('0')||!validSchedule();
  $('#auto-sync').setAttribute('aria-checked',String(state.auto_sync===true));
}
async function call(name,...args){
  if(!apiReady){toast(t('runApp'),true);return {ok:false}}
  localBusy=true;updateDisabled();
  try{const result=await window.pywebview.api[name](...args);if(result&&!result.ok)toast(translateError(result.error)||t('failed'),true);else if(name==='save_log')toast(t('saved',{path:result.path}));return result;}
  catch(e){toast(String(e),true);return {ok:false}}
  finally{localBusy=false;await poll();updateDisabled()}
}
function effectiveSwitch(key){return Object.hasOwn(state.requested||{},'switches:'+key)?state.requested['switches:'+key]:state.snapshot?.switches[key]}
function drawToggle(el,key){const v=effectiveSwitch(key),pending=Object.hasOwn(state.requested||{},'switches:'+key);el.setAttribute('aria-checked',String(v===true));el.classList.toggle('unknown',v==null);el.title=t(pending?'pending':'fromClock');if(el.classList.contains('channel')){el.classList.toggle('on',v===true);el.querySelector('small').textContent=t(v==null?'unknown':v?'on':'off')+(pending?' · '+t('pending'):'')}}
function hex(rgb){return '#'+rgb.map(v=>v.toString(16).padStart(2,'0')).join('')}
function drawState(){
  const s=state.snapshot;
  document.querySelectorAll('[data-switch]').forEach(el=>drawToggle(el,el.dataset.switch));
  drawToggle($('#schedule-toggle'),'0');
  featureKeys.forEach(key=>{const v=effectiveSwitch(key),pending=Object.hasOwn(state.requested||{},'switches:'+key),el=$(`[data-setting-state="${key}"]`);el.classList.toggle('uncertain',v==null||pending);el.textContent=v==null?(s?t('rawUnknown',{raw:s.raw_switches[key]}):t('unread')):t(v?'on':'off')+' · '+t(pending?'pending':'fromClock')});
  $('#color-hex').textContent=s?hex(s.rgb).toUpperCase():t('unread');$('#color-chip').style.background=s?hex(s.rgb):'';
  $('#color-origin').textContent=t(state.requested?.rgb?'lastReply':s?'fromClock':'unread');
  if(!draftDirty&&(state.requested?.rgb||s?.rgb))setDraft(hex(state.requested?.rgb||s.rgb),false);else updateDraftLabel();
  for(const kind of ['alarm1','alarm2']){const input=$(`[data-time="${kind}"]`),requested=state.requested?.['times:'+kind],value=s?.times[kind];if(!input.dataset.dirty&&document.activeElement!==input)input.value=requested??value??'';$(`[data-time-warning="${kind}"]`).textContent=requested?t('timeSent',{value:requested}):value?t('timeReply',{value}):s?t('invalidTime',{value:s.raw_times[kind]}):t('unread')}
  if(!scheduleEditing){for(const kind of ['on','off']){const input=$('#schedule-'+kind);if(document.activeElement!==input)input.value=state.schedule?.[kind]||s?.times[kind]||''}}
  updateScheduleLabels();
}
function validSchedule(){return ['on','off'].every(k=>/^(?:[01]\d|2[0-3]):[0-5]\d$/.test($('#schedule-'+k).value))}
function updateScheduleLabels(){
  const on=$('#schedule-on').value,off=$('#schedule-off').value;
  $('#schedule-local').textContent=on&&off?t('scheduleSaved',{on,off}):t('scheduleEmpty');
  const r=state.requested||{},s=state.snapshot;
  $('#schedule-state').textContent=r['times:on']||r['times:off']?t('scheduleSent',{on:r['times:on']||s?.times.on||'—',off:r['times:off']||s?.times.off||'—'}):s?t('scheduleRead',{on:s.raw_times.on,off:s.raw_times.off}):t('unread');
}
function renderDevices(){
  const box=$('#device-list');box.replaceChildren();
  if(!state.devices?.length){const empty=document.createElement('div');empty.className='empty';empty.textContent=t(state.busy?'scanning':'scanPrompt');box.append(empty);return}
  if(!selectedDevice){selectedDevice=state.devices.find(d=>d.likely)?.address||null}
  for(const d of state.devices){const b=document.createElement('button');b.className='device-option'+(selectedDevice===d.address?' selected':'');const label=document.createElement('div'),name=document.createElement('strong'),address=document.createElement('small'),rssi=document.createElement('small');name.textContent=d.name==='Без имени'?t('unnamed'):d.name;address.textContent=d.address;rssi.textContent=d.rssi+' dBm';label.append(name,address);b.append(label,rssi);b.onclick=()=>{selectedDevice=d.address;renderDevices();updateDisabled()};box.append(b)}
}
function updateState(next){
  const previous=state;state=next;
  if(language!==state.language)applyLanguage(state.language||'ru');
  applyTheme(state.theme);$('#status').textContent=state.status;$('#dialog-status').textContent=state.status;
  $('#connection-dot').classList.toggle('connected',state.connected);$('#connection-label').textContent=t(state.connected?'connected':'connect');$('#device-name').textContent=state.device_name;
  const label=state.snapshot_at?t('readAt',{time:state.snapshot_at})+(!state.connected?' · '+t('stale'):''):t('unread');$('#snapshot-state').textContent=label;$('#read-time').textContent=label;
  drawState();if(state.error&&state.error!==previous.error)toast(state.error,true);
  if(JSON.stringify(state.devices)!==JSON.stringify(previous.devices)||state.busy!==previous.busy)renderDevices();
  const text=state.logs?.map(line=>{const prefix=line.slice(0,9),body=line.slice(9);return prefix+translateError(body)}).join('\n')||t('noEvents');
  if($('#journal').textContent!==text){const bottom=$('#journal').scrollHeight-$('#journal').scrollTop-$('#journal').clientHeight<60;$('#journal').textContent=text;if(bottom)$('#journal').scrollTop=$('#journal').scrollHeight}
  if(connectingAttempt&&!state.busy){if(state.connected&&$('#connect-dialog').open)$('#connect-dialog').close();connectingAttempt=false}updateDisabled();
}
async function poll(){if(!apiReady||pollRunning)return;pollRunning=true;try{updateState(await window.pywebview.api.poll())}catch(e){$('#status').textContent=t('lost',{error:String(e)})}finally{pollRunning=false}}
function updateDraftLabel(){$('#draft-label').textContent=t(draftDirty?'selected':'colorValue',{color:draftColor.toUpperCase()})}
function setDraft(color,dirty=true){draftColor=color;draftDirty=dirty;$('#custom-color').value=color;updateDraftLabel();document.querySelectorAll('.preset').forEach(b=>b.classList.toggle('selected',b.dataset.color===color.toLowerCase()))}
function hueToHex(h){let x=1-Math.abs((h/60)%2-1),rgb=h<60?[1,x,0]:h<120?[x,1,0]:h<180?[0,1,x]:h<240?[0,x,1]:h<300?[x,0,1]:[1,0,x];return hex(rgb.map(v=>Math.round(v*255)))}
document.querySelectorAll('[data-color]').forEach(b=>b.onclick=()=>setDraft(b.dataset.color));$('#hue').oninput=e=>setDraft(hueToHex(+e.target.value));$('#custom-color').oninput=e=>setDraft(e.target.value);
$('#apply-color').onclick=async()=>{if((await call('set_color',draftColor))?.ok)draftDirty=false};
document.querySelectorAll('[data-switch]').forEach(b=>b.onclick=()=>call('set_switch',b.dataset.switch,effectiveSwitch(b.dataset.switch)!==true));
document.querySelectorAll('[data-time]').forEach(input=>input.oninput=()=>input.dataset.dirty='1');document.querySelectorAll('[data-save-time]').forEach(b=>b.onclick=async()=>{const input=$(`[data-time="${b.dataset.saveTime}"]`);if(!input.value){toast(t('scheduleEmpty'),true);return}if((await call('set_time',b.dataset.saveTime,input.value))?.ok)delete input.dataset.dirty});
function saveScheduleDraft(){
  scheduleEditing=true;const on=$('#schedule-on').value,off=$('#schedule-off').value;updateScheduleLabels();updateDisabled();
  if(!apiReady)return;
  scheduleSave=scheduleSave.then(async()=>{const result=await window.pywebview.api.save_schedule(on,off);if(!result.ok)throw new Error(translateError(result.error));}).catch(e=>{toast(String(e),true)});
}
for(const kind of ['on','off'])$('#schedule-'+kind).onchange=()=>{scheduleSave=scheduleSave.catch(()=>{});saveScheduleDraft()};
async function applySchedule(enabled){
  if(enabled&&!validSchedule()){toast(t('scheduleEmpty'),true);return}
  const on=$('#schedule-on').value,off=$('#schedule-off').value;
  try{await scheduleSave;if(enabled){const result=await call('save_schedule',on,off);if(!result?.ok)return}await call('apply_schedule',on,off,enabled)}catch(e){toast(String(e),true)}
}
$('#schedule-toggle').onclick=()=>applySchedule(effectiveSwitch('0')!==true);$('#schedule-apply').onclick=()=>applySchedule(true);
function openMenuReference(){showPage('home');$('#remote-reference').hidden=false;$('#page-home').classList.add('menu-open');document.querySelectorAll('[data-open-menu]').forEach(b=>b.setAttribute('aria-expanded','true'));$('.remote-card').scrollIntoView({block:'start'});}
document.querySelectorAll('[data-open-menu]').forEach(b=>b.onclick=openMenuReference);
$('#close-menu-reference').onclick=()=>{$('#remote-reference').hidden=true;$('#page-home').classList.remove('menu-open');document.querySelectorAll('[data-open-menu]').forEach(b=>b.setAttribute('aria-expanded','false'));$('.remote-card [data-open-menu]').focus()};
document.querySelectorAll('[data-key]').forEach(b=>b.onclick=()=>{if(b.dataset.key==='K07')openMenuReference();return call('remote_key',b.dataset.key)});$('#refresh').onclick=()=>call('refresh');$('#sync-once').onclick=()=>call('sync_time');$('#auto-sync').onclick=()=>call('set_auto_sync',!state.auto_sync);$('#save-log').onclick=()=>call('save_log');$('#connection-button').onclick=()=>$('#connect-dialog').showModal();$('#close-dialog').onclick=()=>$('#connect-dialog').close();$('#scan').onclick=()=>{selectedDevice=null;call('scan')};$('#enable-bt').onclick=()=>call('enable_bluetooth');$('#connect').onclick=async()=>{connectingAttempt=true;if(!(await call('connect',selectedDevice,$('#password').value))?.ok)connectingAttempt=false};$('#disconnect').onclick=()=>call('disconnect');
function clockTick(){const now=new Date(),locale=language==='en'?'en-GB':'ru-RU';$('#computer-time').textContent=now.toLocaleTimeString(locale,{hour12:false});$('#computer-date').textContent=now.toLocaleDateString(locale,{weekday:'long',day:'numeric',month:'long',year:'numeric'})}
function applyTheme(theme){document.documentElement.dataset.theme=theme||'light';$('#theme-toggle').textContent=(theme==='dark'?'☀ ':'☾ ')+t(theme==='dark'?'lightTheme':'darkTheme');$('#theme-toggle').setAttribute('aria-pressed',String(theme==='dark'))}
$('#theme-toggle').onclick=()=>call('set_theme',state.theme==='dark'?'light':'dark');$('#language').onchange=async e=>{const result=await call('set_language',e.target.value);if(!result?.ok)$('#language').value=language};
applyLanguage('ru');updateDisabled();clockTick();setInterval(clockTick,1000);
window.addEventListener('pywebviewready',()=>{apiReady=true;poll();setInterval(poll,500)});
