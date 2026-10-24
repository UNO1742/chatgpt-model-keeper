import copy
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
import app
import github_updates as updates
from runtime_cache import ensure_runtime
from desktop import validate_config

class Response(io.BytesIO):
    def __enter__(self):return self
    def __exit__(self,*args):self.close()

class Services(unittest.TestCase):
    def test_versions(self):
        self.assertGreater(updates.version('v2.1.0'),updates.version('2.0.9'))
        with self.assertRaises(ValueError):updates.version('v2.0.0-rc')
    def test_release_checks(self):
        body={'draft':False,'prerelease':False,'tag_name':'v2.1.0','assets':[{'name':updates.ASSET,'browser_download_url':f'https://github.com/{updates.REPO}/releases/download/v2.1.0/{updates.ASSET}','digest':'sha256:'+'a'*64,'size':3}]}
        with patch('urllib.request.urlopen',return_value=Response(json.dumps(body).encode())):
            self.assertTrue(updates.latest('2.0.0')['newer'])
        body['assets'][0]['browser_download_url']='https://example.com/setup.exe'
        with patch('urllib.request.urlopen',return_value=Response(json.dumps(body).encode())):
            with self.assertRaises(ValueError):updates.latest('2.0.0')
    def test_download_digest_failure_never_leaves_installer(self):
        release={'url':f'https://github.com/{updates.REPO}/releases/download/v2.1.0/{updates.ASSET}','sha256':'a'*64,'size':3}
        with tempfile.TemporaryDirectory() as directory:
            with patch('urllib.request.urlopen',return_value=Response(b'bad')):
                with self.assertRaises(ValueError):updates.download(release,Path(directory))
            self.assertEqual(list(Path(directory).iterdir()),[])
    def test_runtime_cache_verifies_and_reuses(self):
        with tempfile.TemporaryDirectory() as directory:
            base=Path(directory);assets=base/'assets';assets.mkdir();body=b'renderer'
            manifest={'files':[{'path':'horizon.mjs','url':'https://chatgpt.com/cdn/test.js','size':len(body),'sha256':hashlib.sha256(body).hexdigest()}]}
            (assets/'runtime_manifest.json').write_text(json.dumps(manifest))
            with patch('urllib.request.urlopen',return_value=Response(body)) as fetch:
                ensure_runtime(base,assets);ensure_runtime(base,assets);self.assertEqual(fetch.call_count,1)
    def test_form_validation(self):
        self.assertEqual(validate_config(copy.deepcopy(app.DEFAULT)),app.DEFAULT)
        broken=copy.deepcopy(app.DEFAULT);broken['work']['model']=''
        with self.assertRaises(ValueError):validate_config(broken)
        broken=copy.deepcopy(app.DEFAULT);broken['chat']['effort']='made-up'
        with self.assertRaises(ValueError):validate_config(broken)

if __name__=='__main__':unittest.main()
