/* Bridge to the pinned webpage PowerSlider and its original React/Radix/Motion
   dependencies. The export shim exposes H; its implementation is not rewritten. */
const chunks=['226913.f2de3ceb87','337882.a886ddfe75','257798.f8dfab4d2e','673108.b00e716df0','396705.4dac4581d5'];
let enginePromise;
export function initialize(){return enginePromise??=loadEngine();}
async function loadEngine(){
  const definitions=Object.assign({},...(await Promise.all(chunks.map(name=>import('../runtime/component/'+name+'.mjs')))).map(chunk=>chunk.__webpack_modules__));
  const cache={},loaded=[];
  function require(id){
    if(cache[id])return cache[id].exports;
    if(!definitions[id])throw Error('原组件依赖缺失：'+id);
    const module=cache[id]={id,exports:{}};loaded.push(id);
    try{definitions[id](module,module.exports,require);}catch(error){delete cache[id];throw error;}
    return module.exports;
  }
  require.d=(target,getters={},values={})=>{for(const[key,get]of Object.entries(getters))if(!Object.hasOwn(target,key))Object.defineProperty(target,key,{get,enumerable:true});for(const[key,value]of Object.entries(values))if(!Object.hasOwn(target,key))Object.defineProperty(target,key,{value,enumerable:true});};
  require.o=(value,key)=>Object.hasOwn(value,key);
  require.n=value=>{const getter=value?.__esModule?()=>value.default:()=>value;require.d(getter,{a:getter});return getter;};
  require.r=target=>{Object.defineProperty(target,Symbol.toStringTag,{value:'Module'});Object.defineProperty(target,'__esModule',{value:true});};
  require.nmd=module=>(module.paths=[],module.children??=[],module);
  require.g=globalThis;require.p=new URL('../runtime/',import.meta.url).href;require.m=definitions;
  require.t=function(value,mode){if(mode&1)value=require(value);if(mode&8)return value;if(value&&typeof value==='object'&&((mode&4)&&value.__esModule||(mode&16)&&typeof value.then==='function'))return value;const result=Object.create(null);require.r(result);const getters={};if(mode&2)for(let object=value;object&&object!==Object.prototype&&object!==Function.prototype;object=Object.getPrototypeOf(object))for(const key of Object.getOwnPropertyNames(object))getters[key]=()=>value[key];getters.default=()=>value;require.d(result,getters);return result;};
  require.e=()=>Promise.reject(Error('不加载账号或业务模块'));
  // Only dependencies actually used by the independent slider are evaluated.
  const lazy=id=>new Proxy({}, {get:(_,key)=>require(id)[key]});Object.assign(lazy,require);
  const source=definitions.RWnX?.toString(),marker='n.d(t,{a:()=>eN});';
  if(!source?.includes(marker))throw Error('原滑条组件导出已变化');
  const factory=Function('return ('+source.replace(marker,'n.d(t,{a:()=>eN,OriginalSlider:()=>H});')+')')();
  const exports={};factory({exports},exports,lazy);
  const React=require('zd8w'),ReactDOM=require('i5yi');
  const engine={React,ReactDOM,flushSync:require('v7qY').flushSync,Component:exports.OriginalSlider,loaded};
  window.originalSliderEngine={module:'RWnX',component:'H',dependencies:'original React/Radix/Motion',loaded};
  return engine;
}
export async function mount(element,{options,selected,onChange}){
  const {React,ReactDOM,flushSync,Component}=await initialize();
  const originalOptions=options.map(([id,label])=>({id,label,isLocked:false,isMax:false,requiresExplicitSelection:false}));
  let setSelection,refreshFocus,current=selected;
  let mounted,rejected;
  const ready=new Promise((resolve,reject)=>{mounted=resolve;rejected=reject;});
  function notify(option){if(current===option.id)return;current=option.id;setSelection(option.id);onChange(option.id);}
  function Bound(){
    const [value,set]=React.useState(selected),[focused,setFocused]=React.useState(false);
    setSelection=set;refreshFocus=setFocused;
    React.useLayoutEffect(()=>{mounted();},[]);
    return React.createElement(Component,{active:true,fastModeEnabled:false,initialOptionId:selected,selectedOptionId:value,options:originalOptions,keyboardControlFocused:focused,onSelectOption:notify,onCommitOption:notify});
  }
  const root=ReactDOM.createRoot(element,{onUncaughtError:rejected});root.render(React.createElement(Bound));
  await ready;
  element.dataset.renderer='original-RWnX-H';
  return {select(id){if(!originalOptions.some(option=>option.id===id))throw Error('不支持的档位');current=id;flushSync(()=>setSelection(id));},focus(yes){refreshFocus(yes);},dispose(){root.unmount();}};
}
