"""Read-only polling/download for an already submitted trial. No retry of inference."""
import argparse,json,time,urllib.request,io,wave,hashlib
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--trial',choices=['A','B','C'],required=True);p.add_argument('--private-dir',type=Path,required=True);a=p.parse_args()
root=a.private_dir;submitted=json.loads((root/('trial-'+a.trial+'-submission.json')).read_text());ident=submitted['id'];base='http://192.168.1.127:17493';start=time.monotonic();last=None
while time.monotonic()-start<(960 if a.trial=='A' else 360):
 with urllib.request.urlopen(base+'/history/'+ident,timeout=15) as response:row=json.load(response)
 (root/('trial-'+a.trial+'-history.json')).write_text(json.dumps(row));status=row.get('status') or 'completed'
 if status!=last:print(json.dumps({'trial':a.trial,'status':status,'observed_seconds':round(time.monotonic()-start,1),'error':row.get('error')}),flush=True);last=status
 if status in ['completed','failed','cancelled']:
  result={'id':ident,'trial':a.trial,'success':status=='completed','status':status,'error':row.get('error'),'observer_seconds':time.monotonic()-start,'audio_url':base+'/audio/'+ident if status=='completed' else None}
  if result['success']:
   with urllib.request.urlopen(result['audio_url'],timeout=20) as response:audio=response.read()
   with wave.open(io.BytesIO(audio)) as wav:
    assert wav.getnchannels()==1 and wav.getframerate()==24000 and wav.getnframes()>0
    result.update(wav_seconds=wav.getnframes()/wav.getframerate(),sample_rate=wav.getframerate(),wav_frames=wav.getnframes(),wav_bytes=len(audio),wav_sha256=hashlib.sha256(audio).hexdigest())
   (root/('Eduardo-D087-'+a.trial+'.wav')).write_bytes(audio)
  (root/('trial-'+a.trial+'-observed.json')).write_text(json.dumps(result));print(json.dumps(result),flush=True);raise SystemExit(0 if result['success'] else 1)
 time.sleep(5)
# Bounded engine supervisor remains authoritative; do not submit another job.
raise TimeoutError('Observation budget exceeded: inspect/cancel this existing job; never resubmit automatically')
