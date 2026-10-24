const HOST = 'local.chatgpt.modelkeeper';
let port, sequence = 0;
const pending = new Map();
function connect() {
  if (port) return port;
  port = chrome.runtime.connectNative(HOST);
  port.onMessage.addListener(message => {
    const p = pending.get(message.id);
    if (p) { clearTimeout(p.timer); pending.delete(message.id); p.resolve(message); }
  });
  port.onDisconnect.addListener(() => {
    const error = chrome.runtime.lastError?.message || '本机程序连接断开';
    port = null;
    for (const p of pending.values()) { clearTimeout(p.timer); p.resolve({error}); }
    pending.clear();
  });
  return port;
}
chrome.runtime.onMessage.addListener((message, sender, reply) => {
  if (!sender.tab || !sender.url?.startsWith('https://chatgpt.com/') || message.type !== 'sync') return;
  const id = ++sequence;
  const timer = setTimeout(() => { pending.delete(id); reply({error:'本机程序连接超时，请检查安装。'}); }, 8000);
  pending.set(id,{resolve:reply,timer});
  try {
    connect().postMessage({id, type:'status', tab:sender.tab.id, report:message.report});
  } catch (e) {
    clearTimeout(timer); pending.delete(id); reply({error:String(e)});
  }
  return true;
});
