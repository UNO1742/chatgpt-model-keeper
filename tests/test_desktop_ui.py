"""Own settings UI: rounded card, visible slider transition and bridge actions."""
import copy
import json
from pathlib import Path
import sys
import threading
from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
from functools import partial
from playwright.sync_api import sync_playwright
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app

def run():
    base=Path(__file__).resolve().parents[1]
    initial={'type':'initial','config':app.DEFAULT,'startup':True,'version':app.VERSION,'models':app.MODELS,'efforts':app.EFFORTS}
    class Quiet(SimpleHTTPRequestHandler):
        def log_message(self,*args):pass
    server=ThreadingHTTPServer(('127.0.0.1',0),partial(Quiet,directory=str(base/'desktop_ui')))
    threading.Thread(target=server.serve_forever,daemon=True).start()
    try:
        with sync_playwright() as p:
            browser=p.chromium.launch();page=browser.new_page(viewport={'width':360,'height':650})
            errors=[];page.on('pageerror',lambda e:errors.append(str(e)))
            page.add_init_script('window.initial='+json.dumps(initial)+';window.qt={webChannelTransport:{}};window.requests=[];window.QWebChannel=function(t,callback){callback({objects:{bridge:{message:{connect(fn){window.incoming=fn}},request(raw){const m=JSON.parse(raw);requests.push(m);if(m.action==="ready")incoming(JSON.stringify(initial));}}}})};')
            page.goto(f'http://127.0.0.1:{server.server_port}/index.html?view=settings')
            page.wait_for_function('document.querySelector("#chat-model").value==="GPT-6"')
            assert page.locator('#card').evaluate('e=>getComputedStyle(e).borderRadius')=='28px'
            assert page.locator('#card').evaluate('e=>e.getBoundingClientRect().bottom')<=650
            page.locator('#chat-model').fill('GPT-5.6 Sol')
            page.locator('[data-mode=work]').click();page.wait_for_timeout(80)
            midway=page.locator('.thumb').evaluate('e=>getComputedStyle(e).transform')
            page.wait_for_timeout(250)
            finish=page.locator('.thumb').evaluate('e=>getComputedStyle(e).transform')
            assert midway!=finish,(midway,finish)
            assert page.locator('[data-pane=work]').evaluate('e=>getComputedStyle(e).opacity')=='1'
            page.locator('#work-effort').select_option('high');page.locator('#save').click()
            saved=page.evaluate('requests.findLast(x=>x.action==="save").data')
            assert saved['config']['chat']['model']=='GPT-5.6 Sol'
            assert saved['config']['work']['effort']=='high'
            print('PASS rounded card fits window; slider visibly transitions; both presets survive switching')
            page.locator('#extension').click();assert page.locator('#guide').is_visible()
            assert page.evaluate('requests.some(x=>x.action==="copyExtension")')
            page.locator('#open-folder').click();assert page.evaluate('requests.some(x=>x.action==="openExtension")')
            page.locator('#guide-close').click();assert not page.locator('#guide').is_visible()
            print('PASS extension installation guide explains one-time loading and separate folder action')
            page.evaluate('incoming(JSON.stringify({type:"release",release:{newer:true,tag:"v2.1.0"}}));incoming(JSON.stringify(initial));')
            assert page.locator('#version').text_content()=='v'+app.VERSION
            page.locator('#update').click();assert page.evaluate('requests.some(x=>x.action==="installUpdate")')
            assert not errors,errors
            print('PASS GitHub update button retains version UI and dispatches update action')
            browser.close()
    finally:server.shutdown();server.server_close()

if __name__=='__main__':run()
