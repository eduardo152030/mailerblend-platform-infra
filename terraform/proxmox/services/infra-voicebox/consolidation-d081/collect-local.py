"""Collect terminal D081 evidence and private WAV/checkpoint; no inference retries."""
from pathlib import Path
import subprocess,json,uuid,urllib.request,wave,hashlib,tarfile,sys
p=Path.home()/'.local/share/mailerblend-recovery/voicebox-d081';ident=json.loads((p/'submission.json').read_text())['id'];job=uuid.UUID(ident).hex
ssh=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve']
r=subprocess.run(ssh+['python3 - '+job],input=(Path(__file__).parent/'collect.py').read_text(),text=True,capture_output=True,check=True);(p/'job-final.private.json').write_text(r.stdout);data=json.loads(r.stdout)
if data['state.json']['status']!='completed':print(json.dumps(data['state.json']));sys.exit(1)
history=json.load(urllib.request.urlopen('http://192.168.1.127:17493/history/'+ident));(p/'history.private.json').write_text(json.dumps(history));assert history['status']=='completed'
raw=urllib.request.urlopen('http://192.168.1.127:17493/audio/'+ident,timeout=30).read();wav=p/'Eduardo-D081-continuo.wav';wav.write_bytes(raw);wav.chmod(0o600)
with wave.open(str(wav)) as w:result={'seconds':w.getnframes()/w.getframerate(),'frames':w.getnframes(),'rate':w.getframerate(),'channels':w.getnchannels(),'sample_width':w.getsampwidth(),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),'url':'http://192.168.1.127:17493/audio/'+ident}
assert result['rate']==24000 and result['channels']==1 and result['sample_width']==2
(p/'wav.json').write_text(json.dumps(result))
with (p/'job-complete.tar').open('xb') as f:subprocess.run(ssh+['pct exec 627 -- tar -C /srv/voicebox/qwen-worker/jobs -cf - '+job],stdout=f,check=True)
(p/'job-complete.tar').chmod(0o600);restore=p/'restore-job';restore.mkdir(mode=0o700,exist_ok=False)
with tarfile.open(p/'job-complete.tar') as t:
 for m in t.getmembers():assert not Path(m.name).is_absolute() and '..' not in Path(m.name).parts and (m.isfile() or m.isdir())
 t.extractall(restore)
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'pilot-d077'));from checkpoint import load_checkpoint
codes,meta=load_checkpoint(restore/job/'checkpoint');assert meta['text_sha256']=='a29d9c360200ef3277ea5a6f7ccbeff03cf763deef9df32373fb7ee7b10c413c'
(p/'checkpoint-backup-verified.json').write_text(json.dumps({'recoverable_from_new_process':True,'shape':list(codes.shape),'dtype':str(codes.dtype),'eos':meta['generation']['eos_emitted'],'tar_sha256':hashlib.sha256((p/'job-complete.tar').read_bytes()).hexdigest()}))
for name in ['talker-supervisor.json','decoder-supervisor.json']:
 x=data[name];rows=x['measurements'];baseline=x['baseline'];last=x['after'];summary={'elapsed':x['elapsed_total'],'success':x.get('success'),'peak_ct':max(r['ct_current'] for r in rows),'peak_rss':max(r.get('rss_bytes',0) for r in rows),'peak_worker':max(r.get('worker_current',0) for r in rows),'peak_ct_anon':max(r['ct_stat']['anon'] for r in rows),'peak_ct_file':max(r['ct_stat']['file'] for r in rows),'peak_ct_kernel':max(r['ct_stat']['kernel'] for r in rows),'peak_swap':max(r['ct_swap'] for r in rows),'peak_ct_psi':max(r['ct_psi_full_avg10'] for r in rows),'min_host_available':min(r['host_available'] for r in rows),'oom_delta':last['host_oom']-baseline['host_oom'],'ct_events_before':baseline['ct_events'],'ct_events_after':last['ct_events'],'cpu_seconds':(last['ct_cpu']['usage_usec']-baseline['ct_cpu']['usage_usec'])/1e6};(p/name.replace('.json','-summary.json')).write_text(json.dumps(summary))
print(json.dumps(result))
