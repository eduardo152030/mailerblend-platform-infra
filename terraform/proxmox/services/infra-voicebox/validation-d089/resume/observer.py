"""Read-only API observer: transport failures never alter or re-submit a job."""
from pathlib import Path
import argparse,hashlib,io,json,os,re,subprocess,time,urllib.request,uuid,wave
BASE='http://192.168.1.127:17493'
SSH=['ssh','-o','UserKnownHostsFile=/home/jainer/.ssh/known_hosts','-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
REMOTE='''import sys,urllib.request
path=sys.argv[1]
with urllib.request.urlopen('http://192.168.1.127:17493'+path,timeout=20) as response:
 assert response.status==200
 sys.stdout.buffer.write(response.read())
'''
def safe_path(path):
 if path in ['/health','/tts-capabilities']:return path
 if not re.fullmatch(r'/(history|audio)/[a-f0-9-]{36}',path):raise ValueError('Read-only endpoint required')
 uuid.UUID(path.rsplit('/',1)[1]);return path
def direct_get(path):
 request=urllib.request.Request(BASE+safe_path(path),method='GET')
 with urllib.request.urlopen(request,timeout=15) as response:
  assert response.status==200;return response.read()
def pve_get(path):
 result=subprocess.run(SSH+['python3','-',safe_path(path)],input=REMOTE.encode(),capture_output=True,timeout=40)
 if result.returncode:raise ConnectionError('PVE read-only API request failed')
 return result.stdout
def read_api(path,via='pve',direct=direct_get,pve=pve_get):
 safe_path(path)
 if via=='pve':return pve(path),{'transport':'pve-ssh-strict-http','fallback':False}
 try:return direct(path),{'transport':'direct-http','fallback':False}
 except (OSError,ConnectionError) as exc:
  data=pve(path)
  return data,{'transport':'pve-ssh-strict-http','fallback':True,'direct_error_type':type(exc).__name__}
def save(path,data):
 tmp=path.with_suffix('.partial')
 with tmp.open('w') as f:os.chmod(tmp,0o600);json.dump(data,f);f.flush();os.fsync(f.fileno())
 os.replace(tmp,path)
def wav_seconds(audio):
 with wave.open(io.BytesIO(audio)) as w:
  assert w.getnchannels()==1 and w.getframerate()==24000 and w.getsampwidth()==2 and w.getnframes()>0
  assert len(w.readframes(w.getnframes()))==w.getnframes()*w.getnchannels()*w.getsampwidth(),'Truncated WAV'
  return w.getnframes()/w.getframerate()
def observe(ident,root,via='pve',budget=360):
 ident=str(uuid.UUID(ident));root=Path(root);assert root.is_dir() and root.stat().st_mode&0o077==0
 assert not (root/'verified.json').exists(),'Evidence already verified; no overwrite'
 started=time.monotonic();last=None;transports=[]
 while time.monotonic()-started<budget:
  try:
   raw,route=read_api('/history/'+ident,via);transports.append(route);row=json.loads(raw)
   save(root/'history.private.json',row);status=row.get('status') or 'completed'
   if status!=last:print(json.dumps({'id':ident,'api_status':status,'route':route}),flush=True);last=status
   if status in ['failed','cancelled']:
    result={'id':ident,'worker_api_terminal':status,'observation':'verified','success':False,'generation_state_modified':False,'inference_submitted':False};save(root/'verified.json',result);return result
   if status=='completed':
    audio,route=read_api('/audio/'+ident,via);transports.append(route)
    seconds=wav_seconds(audio)
    target=root/'audio.wav'
    with target.open('xb') as f:os.chmod(target,0o600);f.write(audio);f.flush();os.fsync(f.fileno())
    result={'id':ident,'worker_api_terminal':'completed','observation':'verified','success':True,'wav_seconds':seconds,'wav_sha256':hashlib.sha256(audio).hexdigest(),'audio_url':BASE+'/audio/'+ident,'routes':transports,'generation_state_modified':False,'inference_submitted':False};save(root/'verified.json',result);return result
  except (OSError,ConnectionError,subprocess.SubprocessError) as exc:
   # Record an observer failure separately. No failed status write to API or queue.
   save(root/'observer-error.json',{'id':ident,'observation':'unavailable','error_type':type(exc).__name__,'worker_status':'unknown','generation_state_modified':False,'inference_submitted':False});raise
  time.sleep(3)
 save(root/'observer-error.json',{'id':ident,'observation':'timeout','worker_status':'unknown','generation_state_modified':False,'inference_submitted':False});raise TimeoutError('Observation only: never re-submit inference')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--id',required=True);p.add_argument('--private-dir',type=Path,required=True);p.add_argument('--via',choices=['pve','direct'],default='pve');a=p.parse_args();os.umask(0o077);result=observe(a.id,a.private_dir,a.via);print(json.dumps(result));raise SystemExit(0 if result['success'] else 1)
