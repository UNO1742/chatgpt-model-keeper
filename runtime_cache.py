"""Fetch only pinned public rendering resources; no browser session or credentials."""
import hashlib
import json
from pathlib import Path
import os
import urllib.request
from concurrent.futures import ThreadPoolExecutor

def ensure_runtime(root, assets):
    manifest=json.loads((assets/'runtime_manifest.json').read_text(encoding='utf-8'))
    cache=root/'runtime'
    def fetch(entry):
        path=cache/entry['path']
        if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest()==entry['sha256']:
            return
        req=urllib.request.Request(entry['url'],headers={'User-Agent':'ChatGPT-Model-Keeper/2.0'})
        with urllib.request.urlopen(req,timeout=25) as response:
            data=response.read(entry['size']+1)
        if len(data)!=entry['size'] or hashlib.sha256(data).hexdigest()!=entry['sha256']:
            raise ValueError('网页渲染资源未通过完整性校验')
        path.parent.mkdir(parents=True,exist_ok=True)
        temporary=path.with_name(path.name+'.download')
        temporary.write_bytes(data);os.replace(temporary,path)
    with ThreadPoolExecutor(max_workers=4) as pool:
        list(pool.map(fetch,manifest['files']))
    return cache
