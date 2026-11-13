"""Toggle only the verified CB receipt; never restart app, agent or CT."""
from pathlib import Path
import argparse,fcntl,hashlib,json,os,subprocess,sys,time,urllib.request
sys.dont_write_bytecode=True;sys.path.insert(0,'/opt/voicebox-qwen-627')
import supervise,engine_policy
CODE=Path('/opt/voicebox-qwen-627');BACK=Path('/mnt/storage/d089-resume')
def digest(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def get(path):return json.load(urllib.request.urlopen('http://192.168.1.127:17493'+path,timeout=15))
def atom(p,d):
 tmp=p.with_suffix('.partial');tmp.write_text(json.dumps(d,indent=2));tmp.chmod(0o600)
 with tmp.open('rb') as f:os.fsync(f.fileno())
 os.replace(tmp,p)
def main():
 p=argparse.ArgumentParser();p.add_argument('--enable',action='store_true');p.add_argument('--disable',action='store_true');a=p.parse_args();assert a.enable!=a.disable
 receipt=CODE/'chatterbox-release.json';r=json.loads(receipt.read_text());BACK.mkdir(mode=0o700,exist_ok=True)
 if a.enable:
  with open('/run/lock/qwen-d077-627.lock','a') as lock:
   fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
   assert not r['enabled'] and not (BACK/'receipt-before-enable.json').exists(),'Do not repeat activation automatically'
   pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();root=Path('/proc',pid,'root');jobs=root/'srv/voicebox/qwen-worker/jobs'
   assert json.loads((jobs/'27af4ddcc17a4e109dc2b3fe2d569329/state.json').read_text())['status']=='completed'
   assert not any(json.loads(p.read_text()).get('status') in ['running','queued'] for p in jobs.glob('*/state.json'))
   names=supervise.ct('docker','ps','--format','{{.Names}}').splitlines();assert not any(n.startswith(('qwen-','chatterbox-','d089-inference-')) for n in names)
   assert get('/health')['status']=='healthy' and not get('/health')['model_loaded'];caps=get('/tts-capabilities');assert caps['qwen']['ready'] and caps['qwen']['languages']==['es','en']
   assert engine_policy.preflight(supervise.sample())
   for folder,key in [(CODE,'source_hashes'),(jobs.parent/'src','worker_hashes')]:
    for name,h in r[key].items():assert digest(folder/name)==h
   env=root/'srv/voicebox/chatterbox-d085'
   assert digest(env/'environment-receipt.json')==r['environment_receipt_sha256'] and digest(env/'models/manifest.json')==r['model_manifest_sha256']
   for entry in json.loads((env/'models/manifest.json').read_text())['files']:assert digest(env/'models'/entry['name'])==entry['sha256']
   cg=Path('/sys/fs/cgroup/lxc/627');assert int((cg/'memory.max').read_text())==20*2**30 and int((cg/'memory.swap.max').read_text())==2*2**30
   assert engine_policy.CB['worker_stop_bytes']==7*2**30 and engine_policy.CB['worker_hard_bytes']==8*2**30 and engine_policy.CB['timeout_seconds']==300
   assert json.loads(Path('/mnt/storage/d089/backups-verified.json').read_text())['result']=='PASS'
   (BACK/'receipt-before-enable.json').write_bytes(receipt.read_bytes());(BACK/'receipt-before-enable.json').chmod(0o600)
   r.update(enabled=True,reason='D089 resume authorized: Spanish API/hash verified; one English test; acoustic acceptance pending');atom(receipt,r)
 else:
  (BACK/'receipt-before-disable.json').write_bytes(receipt.read_bytes());(BACK/'receipt-before-disable.json').chmod(0o600)
  r.update(enabled=False,reason='D089 resume STOP: English or API verification failed; evidence preserved');atom(receipt,r)
 for _ in range(30):
  caps=get('/tts-capabilities')
  if caps['chatterbox']['ready']==a.enable and caps['qwen']['ready']:break
  time.sleep(.5)
 else:raise RuntimeError('Readiness not confirmed')
 print(json.dumps({'enabled':a.enable,'capabilities':caps,'service_restarts':0,'model_loads':0}))
if __name__=='__main__':main()
