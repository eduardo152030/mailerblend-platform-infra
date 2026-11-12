#!/usr/bin/env python3
"""PVE supervisor: one real Voicebox request, finite deadline, rollback on failure."""
import argparse,json,time,urllib.request,subprocess,wave,io,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--label',choices=['short','trading','minute'],required=True);p.add_argument('--existing-id');a=p.parse_args();root=Path('/root/voicebox-d071');out=root/('api-'+a.label);out.mkdir(mode=0o700,exist_ok=False);CG=Path('/sys/fs/cgroup/lxc/627')
def api(path,value=None):
 req=urllib.request.Request('http://192.168.1.127:17493'+path,data=None if value is None else json.dumps(value).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=12) as r:return json.load(r)
def measure():
 return {'elapsed_seconds':time.monotonic()-start,'memory_current':int((CG/'memory.current').read_text()),'swap':int((CG/'memory.swap.current').read_text()),'cpu':(CG/'cpu.stat').read_text(),'events':dict(x.split() for x in (CG/'memory.events').read_text().splitlines()),'host_available':int(next(x.split()[1] for x in Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:')))*1024,'host_pressure':Path('/proc/pressure/memory').read_text()}
start=time.monotonic();b=measure();result={'status':'IN_PROGRESS','measurements':[],'label':a.label};ident=None
try:
 assert api('/worker/health')['status']=='healthy'
 assert b['host_available']>1.5*2**30 and float(b['host_pressure'].splitlines()[1].split()[1].split('=')[1])<2,'Preflight host pressure'
 text=json.loads((root/'test-texts.json').read_text())[a.label]
 g=api('/history/'+a.existing_id) if a.existing_id else api('/generate',{'profile_id':'1fd00418-2a79-4178-883f-af6c3f5e07ee','engine':'openvoice','language':'es','text':text,'personality':False,'max_chunk_chars':200,'normalize':True});ident=g['id'];result['generation_id']=ident
 while time.monotonic()-start<400:
  m=measure();result['measurements'].append(m);(out/'result.json').write_text(json.dumps(result,indent=2))
  assert m['memory_current']<6.5*2**30 and m['swap']-b['swap']<64*2**20,'CT memory/swap safety stop'
  assert m['host_available']>1.5*2**30 and float(m['host_pressure'].splitlines()[1].split()[1].split('=')[1])<2,'Host safety stop'
  assert all(int(m['events'][k])==int(b['events'][k]) for k in ['oom','oom_kill','oom_group_kill']),'OOM stop'
  g=api('/history/'+ident)
  if g['status'] in ['completed','failed','cancelled']:break
  time.sleep(2)
 assert g['status']=='completed',g.get('error','Generation timeout')
 with urllib.request.urlopen('http://192.168.1.127:17493/audio/'+ident,timeout=15) as r:raw=r.read()
 with wave.open(io.BytesIO(raw)) as w:assert w.getnchannels()==1 and w.getsampwidth()==2;seconds=w.getnframes()/w.getframerate();rate=w.getframerate()
 assert seconds>2 and rate==22050
 (out/'audio.wav').write_bytes(raw);result.update(status='TECHNICAL_PASS_PENDING_OWNER_LISTENING',audio_seconds=seconds,generation_seconds=time.monotonic()-start,audio_url='http://192.168.1.127:17493/audio/'+ident,sha256=hashlib.sha256(raw).hexdigest())
except BaseException as e:
 result.update(status='FAIL',reason=str(e))
 if ident:
  try:result['cancel']=api('/generate/'+ident+'/cancel',{})
  except Exception:pass
 subprocess.run(['pct','exec','627','--','bash','/opt/voicebox/pilot-d071/rollback.sh'],check=True,timeout=120);result['rollback']='PASS'
finally:(out/'result.json').write_text(json.dumps(result,indent=2));print(json.dumps({k:v for k,v in result.items() if k!='measurements'}),flush=True)
