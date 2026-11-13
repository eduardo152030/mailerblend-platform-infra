"""One explicitly authorized D087 trial via Voicebox API. Never retries or polls."""
from pathlib import Path
import argparse,json,os,urllib.request,hashlib
TRIALS={
 'A':dict(engine='qwen',language='en',model_size='0.6B',text='This is a test to see if I can speak in English.'),
 'B':dict(engine='chatterbox',language='es',text='Hola, soy Eduardo. Esta es una prueba de mi voz utilizando Chatterbox en español.'),
 'C':dict(engine='chatterbox',language='en',text='Hello, my name is Eduardo. This is a test of my cloned voice using Chatterbox in English.')}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--trial',choices=TRIALS,required=True);p.add_argument('--private-dir',type=Path,required=True);a=p.parse_args()
 os.umask(0o077);root=a.private_dir.resolve();assert root.is_dir() and root.stat().st_mode&0o077==0
 assert json.loads((root/'postdeploy.json').read_text())['result']=='PASS'
 if a.trial!='A':assert json.loads((root/('trial-'+('A' if a.trial=='B' else 'B')+'-validated.json')).read_text())['success'] is True
 body=dict(TRIALS[a.trial],profile_id='1fd00418-2a79-4178-883f-af6c3f5e07ee',seed=42,personality=False,normalize=False,effects_chain=[])
 with (root/('trial-'+a.trial+'-started.json')).open('x') as f:json.dump({'trial':a.trial,'request':body,'automatic_retries':False},f)
 request=urllib.request.Request('http://192.168.1.127:17493/generate',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'},method='POST')
 try:
  with urllib.request.urlopen(request,timeout=30) as response:result=json.load(response)
 except BaseException:
  # Marker stays: HTTP uncertainty requires inspect, never submit again automatically.
  raise
 (root/('trial-'+a.trial+'-submission.json')).write_text(json.dumps(result));print(json.dumps({k:result.get(k) for k in ['id','engine','language','status','created_at']}))
