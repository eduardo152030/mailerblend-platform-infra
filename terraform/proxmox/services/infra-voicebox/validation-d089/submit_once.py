"""Exactly one D089 request per language, via the same API used by Voicebox UI."""
from pathlib import Path
import argparse,json,urllib.request,os
TEXT={'es':'Hola, soy Eduardo. Esta es una prueba de mi voz utilizando Chatterbox en español.','en':'Hello, my name is Eduardo. This is a test of my cloned voice using Chatterbox in English.'}
p=argparse.ArgumentParser();p.add_argument('--language',choices=TEXT,required=True);p.add_argument('--private-dir',type=Path,required=True);a=p.parse_args();root=a.private_dir
os.umask(0o077);assert root.stat().st_mode&0o077==0
assert json.loads((root/'postdeploy.json').read_text())['result']=='PASS'
assert json.loads((root/'control.json').read_text())['all_processes_released']
trial='B' if a.language=='es' else 'C'
if trial=='C':assert json.loads((root/'trial-B-validated.json').read_text())['success']
body={'engine':'chatterbox','language':a.language,'text':TEXT[a.language],'profile_id':'1fd00418-2a79-4178-883f-af6c3f5e07ee','seed':42,'personality':False,'normalize':False,'effects_chain':[]}
with (root/('trial-'+trial+'-started.json')).open('x') as f:json.dump({'request':body,'automatic_retries':False},f)
req=urllib.request.Request('http://192.168.1.127:17493/generate',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'},method='POST')
with urllib.request.urlopen(req,timeout=30) as response:result=json.load(response)
(root/('trial-'+trial+'-submission.json')).write_text(json.dumps(result));print(json.dumps({k:result.get(k) for k in ['id','engine','language','status']}))
