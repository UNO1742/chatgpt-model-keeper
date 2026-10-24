"""Test real DOM events/state transitions against a picker fixture.
Run: python tests/test_adapter.py (requires playwright + chromium).
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import json

BASE=Path(__file__).resolve().parents[1]
SCRIPT=(BASE/'extension/content.js').read_text(encoding='utf-8')
HTML=(BASE/'tests/fixture.html').read_text(encoding='utf-8')

def prepare(browser, chat=None, work=None, setup='', disconnected=False):
    page=browser.new_page()
    page.set_content(HTML)
    cfg={'enabled':True,'chat':chat or {'enabled':True,'model':'GPT-6','effort':'xhigh'},
         'work':work or {'enabled':True,'model':'GPT-6 Sol','effort':'xhigh'}}
    page.evaluate('cfg=>{window.config=cfg;window.reports=[];window.chrome={runtime:{sendMessage:async m=>{reports.push(m.report);return {config:window.config};},onMessage:{addListener:fn=>{window.retry=()=>fn({type:"retry"},null,()=>{});}}}};}',cfg)
    if disconnected:page.evaluate('chrome.runtime.sendMessage=async()=>({error:"Native host not found"})')
    if setup:page.evaluate(setup)
    page.add_script_tag(content=SCRIPT)
    return page

def ready(page):
    page.wait_for_function('window.reports.some(r=>r?.state==="已确认")',timeout=16000)

def failed(page):
    page.wait_for_function('window.reports.some(r=>r?.state==="无法调整")',timeout=16000)

def run():
    with sync_playwright() as p:
        browser=p.chromium.launch()
        page=prepare(browser);ready(page)
        assert page.evaluate('testState.efforts[testState.index]')=='xhigh'
        assert page.get_attribute('#picker','data-selected-reasoning-effort')=='max'
        assert page.locator('[role=menu]').count()==0
        opens=page.evaluate('testState.opens');page.wait_for_timeout(3300)
        assert page.evaluate('testState.opens')==opens
        print('PASS Chinese Chat: visible Extra high despite internal max; idempotence; owned menu closed')
        page.evaluate('setMode("work");testState.lang="en";renderTrigger();retry()');ready(page)
        page.wait_for_function('testState.model==="GPT-6 Sol" && testState.efforts[testState.index]==="xhigh"',timeout=16000)
        page.wait_for_function('document.querySelector("[role=menu]")===null',timeout=16000)
        print('PASS English Work: same-URL mode change, exact model switch and Extra high')
        page.close()
        page=prepare(browser,setup='setMode("work");testState.models=["GPT-6.1 Sol","GPT-6 Astra"]');failed(page)
        assert page.evaluate('testState.model')=='GPT-6.1 Sol'
        print('PASS Unavailable model: no substitution')
        page.close()
        page=prepare(browser,work={'enabled':True,'model':'GPT-6 Astra','effort':'xhigh'},setup='setMode("work");testState.models.push("GPT-6 Astra");testState.locked=true');failed(page)
        assert page.evaluate('testState.model')=='GPT-6.1 Sol'
        print('PASS Locked model: never selected')
        page.close()
        page=prepare(browser,chat={'enabled':True,'model':'GPT-6','effort':'ultra'},setup='testState.efforts=["low","medium","high"];testState.index=1;renderTrigger()');failed(page)
        assert page.evaluate('testState.index')==1
        print('PASS Unsupported effort: restored original position')
        page.close()
        page=prepare(browser,setup='config.enabled=false');page.wait_for_timeout(3300)
        assert page.evaluate('testState.opens')==0
        print('PASS Global pause: no menu operations')
        page.close()
        page=prepare(browser,disconnected=True);page.wait_for_timeout(3300)
        assert page.evaluate('testState.opens')==0
        print('PASS Disconnected native host: no menu operations')
        page.close()
        page=prepare(browser,setup='document.querySelector("[role=group]").remove();document.querySelector("[contenteditable]").setAttribute("aria-label","输入")');page.wait_for_timeout(3300)
        assert page.evaluate('testState.opens')==0
        print('PASS Unknown mode: fail closed')
        page.close()
        # Hidden stale composer does not override the visible Work composer.
        page=prepare(browser,setup='setMode("work");const stale=document.createElement("section");stale.setAttribute("inert","");stale.innerHTML=`<button aria-pressed="true">聊天</button><button data-codex-intelligence-trigger="true">ghost</button>`;document.body.append(stale)');ready(page)
        assert page.evaluate('testState.model')=='GPT-6 Sol'
        print('PASS Hidden stale composer: ignored')
        page.close()
        browser.close()

if __name__=='__main__':run()
