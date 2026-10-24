const isOrb=new URLSearchParams(location.search).get('view')==='orb';
document.querySelector('#orb').hidden=!isOrb;document.querySelector('#card').hidden=isOrb;
let bridge,config,release=null;
const $=s=>document.querySelector(s);
function notice(s){if(!isOrb)$('#status').textContent=s;}
function request(action,data){bridge.request(JSON.stringify({action,data}));}
function fill(data){config=data.config;$('#version').textContent='v'+data.version;$('#enabled').checked=config.enabled;$('#startup').checked=data.startup;for(const mode of ['chat','work']){const p=config[mode];$('#'+mode+'-enabled').checked=p.enabled;$('#'+mode+'-model').value=p.model;$('#'+mode+'-effort').value=p.effort;}}
window.chooseMode=mode=>{const work=mode==='work';$('.segments').classList.toggle('work',work);document.querySelectorAll('[data-mode]').forEach(b=>{const yes=b.dataset.mode===mode;b.classList.toggle('selected',yes);b.setAttribute('aria-selected',String(yes));});document.querySelectorAll('[data-pane]').forEach(p=>p.classList.toggle('active',p.dataset.pane===mode));};
async function startOrb(){
  const {__webpack_modules__}=await import('../runtime/horizon.mjs');
  const blue=[0x35/255,0x66/255,0xf0/255];
  const palette={accentColor:[...blue,1],fallbackColors:['#2854e2','#9ab5f8','#e7efff']};
  const exports={};function require(name){if(name==='IlRO')return {b:()=>palette};throw Error('Unexpected rendering dependency');}
  require.d=(target,map)=>{for(const [name,get]of Object.entries(map))Object.defineProperty(target,name,{get});};
  require.p=new URL('../runtime/',location.href).href;
  __webpack_modules__.HNEj({},exports,require);
  let draws=0;const canvas=$('#voice');
  if(!canvas.getContext('webgl2',{premultipliedAlpha:true}))throw Error('需要支持 WebGL 2 的显卡驱动');
  const controller=await exports.HorizonVoiceOrbController.create(canvas,{displayScale:.98,presentation:'overlay',onDraw:()=>{draws++;window.orbDraws=draws;},onRenderError:()=>request('orbError','原始 WebGL 渲染器无法启动，请检查显卡驱动。')});
  if(!controller)throw Error('网页原始渲染器初始化失败');
  if(document.querySelectorAll('#orb canvas').length!==1){controller.dispose();throw Error('原始 WebGL 渲染失败，已停止简化替代效果');}
  controller.setAudioLevels(null);
  controller.setInputs({paletteIndex:0,phase:'active',previewAudioLevel:0,voiceActivity:'idle'});
  window.orbController=controller;window.addEventListener('pagehide',()=>controller.dispose());
  window.orbKind='HorizonVoiceOrbController/live';
}
new QWebChannel(qt.webChannelTransport,channel=>{
  bridge=channel.objects.bridge;
  bridge.message.connect(raw=>{
    const m=JSON.parse(raw);
    if(m.type==='initial'&&!isOrb){
      $('#models').replaceChildren(...m.models.map(s=>{const o=document.createElement('option');o.value=s;return o;}));
      for(const mode of ['chat','work'])$('#'+mode+'-effort').replaceChildren(...m.efforts.map(([value,label])=>{const o=document.createElement('option');o.value=value;o.textContent=label;return o;}));
      fill(m);notice(m.status||'已准备就绪');
    }
    if(m.type==='status'&&!isOrb){notice(m.text);$('#extension-badge').textContent=m.connected?'已连接':'未连接';$('#extension-badge').classList.toggle('connected',m.connected);}
    if(m.type==='notice')notice(m.text);
    if(m.type==='release'&&!isOrb){release=m.release;$('#update').disabled=false;$('#update-label').textContent=release.newer?'安装更新 '+release.tag:'已是最新版 · '+release.tag;notice(release.newer?'更新来自 GitHub Releases，下载后将校验 SHA-256。':'当前已是 GitHub 最新稳定版。');}
    if(m.type==='updateError'&&!isOrb){$('#update').disabled=false;notice(m.text);}
    if(m.type==='runtimeReady'&&isOrb)startOrb().catch(e=>{$('#orb-error').hidden=false;request('orbError',e.message);});
  });
  if(isOrb){let down=false,moved=false,x=0,y=0;const hit=$('#orb-hit');hit.onpointerdown=e=>{if(e.button!==0)return;down=true;moved=false;x=e.screenX;y=e.screenY;hit.setPointerCapture(e.pointerId);request('dragStart');};hit.onpointermove=e=>{if(down&&Math.abs(e.screenX-x)+Math.abs(e.screenY-y)>4){moved=true;request('dragMove');}};hit.onpointerup=e=>{if(!down)return;down=false;request('dragEnd',{moved});};hit.oncontextmenu=e=>{e.preventDefault();request('context');};}
  else{
    $('[data-mode=chat]').onclick=()=>chooseMode('chat');$('[data-mode=work]').onclick=()=>chooseMode('work');
    $('#close').onclick=()=>request('hide');$('#save').onclick=()=>{const config={enabled:$('#enabled').checked};for(const mode of ['chat','work'])config[mode]={enabled:$('#'+mode+'-enabled').checked,model:$('#'+mode+'-model').value.trim(),effort:$('#'+mode+'-effort').value};request('save',{config,startup:$('#startup').checked});};
    $('#extension').onclick=()=>{$('#guide').hidden=false;request('copyExtension');};$('#guide-close').onclick=()=>$('#guide').hidden=true;$('#copy-path').onclick=()=>request('copyExtension');$('#open-folder').onclick=()=>request('openExtension');
    $('#update').onclick=()=>{if(release?.newer){$('#update').disabled=true;request('installUpdate');}else{$('#update').disabled=true;request('checkUpdate');notice('正在查询 GitHub Releases…');}};
    document.onkeydown=e=>{if(e.key==='Escape')request('hide');};
  }
  request('ready',{orb:isOrb});
});
