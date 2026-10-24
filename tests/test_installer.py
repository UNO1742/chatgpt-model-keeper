"""Windows integration test: isolated installation and Edge profile; restores HKCU.

Run after build.ps1: python tests/test_installer.py
"""
import json
import os
from pathlib import Path
import struct
import subprocess
import tempfile
import time
import winreg
from playwright.sync_api import sync_playwright

BASE=Path(__file__).resolve().parents[1]
HOST_KEY=r'Software\Microsoft\Edge\NativeMessagingHosts\local.chatgpt.modelkeeper'
RUN_KEY=r'Software\Microsoft\Windows\CurrentVersion\Run'
OLD_KEY=r'Software\Microsoft\Windows\CurrentVersion\Uninstall\ChatGPTModelKeeper'
NEW_KEY=r'Software\Microsoft\Windows\CurrentVersion\Uninstall\{E56E50CE-D80C-4D7C-92D7-4FD4647C3652}_is1'

def values(path):
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER,path) as key:
            return [winreg.EnumValue(key,i) for i in range(winreg.QueryInfoKey(key)[1])]
    except FileNotFoundError:return None

def restore(path,items):
    try:winreg.DeleteKey(winreg.HKEY_CURRENT_USER,path)
    except FileNotFoundError:pass
    if items is not None:
        with winreg.CreateKey(winreg.HKEY_CURRENT_USER,path) as key:
            for name,value,kind in items:winreg.SetValueEx(key,name,0,kind,value)

def run():
    snapshots={key:values(key) for key in (HOST_KEY,OLD_KEY,NEW_KEY)}
    startup=next((x for x in values(RUN_KEY) or [] if x[0]=='ChatGPTModelKeeper'),None)
    with tempfile.TemporaryDirectory(prefix='modelkeeper-v2-') as directory:
        root=Path(directory).resolve();target=root/'Programs/ChatGPTModelKeeper'
        env=dict(os.environ,LOCALAPPDATA=str(root),APPDATA=str(root/'Roaming'))
        legacy=root/'ChatGPTModelKeeper';legacy.mkdir()
        config={'enabled':True,'chat':{'enabled':True,'model':'GPT-6','effort':'xhigh'},'work':{'enabled':True,'model':'GPT-6 Sol','effort':'xhigh'}}
        (legacy/'config.json').write_text(json.dumps(config))
        (legacy/'appearance.json').write_text(json.dumps({'theme':'light'}))
        installed=False
        try:
            subprocess.run([str(BASE/'release/ModelKeeper-Setup.exe'),'/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART','/NOICONS','/NOLAUNCH=1',f'/DIR={target}',f'/LOG={root/"install.log"}'],check=True,env=env,timeout=150)
            installed=True
            exe=target/'ModelKeeper.exe';host=target/'ModelKeeperHost.exe'
            assert json.loads((target/'config.json').read_text(encoding='utf-8'))==config
            assert json.loads((target/'appearance.json').read_text(encoding='utf-8'))=={'theme':'light'}
            assert json.loads((target/'host.json').read_text(encoding='utf-8'))['path']==str(host)
            assert values(HOST_KEY)[0][1]==str(target/'host.json')
            assert (target/'extension/manifest.json').exists()
            assert next(x[1] for x in values(RUN_KEY) if x[0]=='ChatGPTModelKeeper')==f'"{exe}" --startup'
            print('PASS Installer: migrated presets, extension, separate host, login startup',flush=True)
            req=json.dumps({'id':7,'type':'config'}).encode()
            process=subprocess.Popen([str(host)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env)
            out,err=process.communicate(struct.pack('<I',len(req))+req,timeout=25)
            assert process.returncode==0 and len(out)>=4,(process.returncode,err)
            size=struct.unpack('<I',out[:4])[0]
            assert json.loads(out[4:4+size])=={'id':7,'config':config}
            print('PASS Installed native executable: binary messaging round trip',flush=True)
            subprocess.run([str(exe),'--autostart','off'],check=True,env=env,timeout=20)
            subprocess.run([str(exe),'--register-installed'],check=True,env=env,timeout=20)
            assert not any(x[0]=='ChatGPTModelKeeper' for x in values(RUN_KEY))
            print('PASS Update registration preserves startup opt-out',flush=True)
            with sync_playwright() as p:
                ext=str(target/'extension')
                context=p.chromium.launch_persistent_context(str(root/'edge'),channel='msedge',headless=True,ignore_default_args=['--disable-extensions'],args=[f'--disable-extensions-except={ext}',f'--load-extension={ext}'],env=env)
                try:
                    context.route('https://chatgpt.com/**',lambda route:route.fulfill(path=str(BASE/'tests/fixture.html'),content_type='text/html'))
                    page=context.pages[0];page.goto('https://chatgpt.com/')
                    page.wait_for_function('testState.efforts[testState.index]==="xhigh"',timeout=35000)
                    page.wait_for_function('document.querySelector("[role=menu]")===null')
                    assert page.get_attribute('#picker','data-selected-reasoning-effort')=='max'
                    page.wait_for_timeout(3200)
                    assert any(r['state']=='已确认' for r in json.loads((target/'status.json').read_text(encoding='utf-8'))['tabs'].values())
                    page.evaluate('setMode("work");testState.lang="en";renderTrigger()')
                    page.wait_for_function('testState.model==="GPT-6 Sol" && testState.efforts[testState.index]==="xhigh"',timeout=35000)
                    config['work']['effort']='high'
                    (target/'config.json').write_text(json.dumps(config))
                    page.wait_for_function('testState.efforts[testState.index]==="high"',timeout=35000)
                    print('PASS Real Edge extension: bilingual Chat/Work selection and live preset reload',flush=True)
                finally:context.close()
            report=BASE.parent/'installed-qt-smoke.json'
            subprocess.run([str(exe),'--gui-smoke',str(report)],check=True,env=env,timeout=65)
            data=json.loads(report.read_text(encoding='utf-8'));orb=json.loads(data['orb'])
            assert data['runtime_ready'] and data['panel_ready'] and not data['errors'] and not data['runtime_error'],data
            assert orb['kind']=='HorizonVoiceOrbController/live' and orb['draws']>10 and orb['canvases']==1,orb
            print(f'PASS Installed original live renderer: {orb["draws"]} draws; rounded settings screenshot',flush=True)
        finally:
            if installed:
                subprocess.run([str(target/'unins000.exe'),'/VERYSILENT','/SUPPRESSMSGBOXES','/NORESTART'],env=env,timeout=120,check=True)
                time.sleep(1)
            for key,items in snapshots.items():restore(key,items)
            with winreg.CreateKey(winreg.HKEY_CURRENT_USER,RUN_KEY) as key:
                if startup:winreg.SetValueEx(key,startup[0],0,startup[2],startup[1])
                else:
                    try:winreg.DeleteValue(key,'ChatGPTModelKeeper')
                    except FileNotFoundError:pass
            print('PASS Test cleanup: original application registration restored',flush=True)

if __name__=='__main__':run()
