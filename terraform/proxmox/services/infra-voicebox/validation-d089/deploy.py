"""CT627-only minimal CB overlay. No app/Qwen image/resource/data changes."""
from pathlib import Path
import argparse,fcntl,hashlib,json,os,shutil,subprocess,time,urllib.request,sys
sys.dont_write_bytecode=True
CODE=Path('/opt/voicebox-qwen-627');BACK=Path('/mnt/storage/d089/deployment');APP='sha256:212703647c03d428adc30f8bf4b864af82690eb41f4fe8ca052ff10dbaa45386'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ct(*a):return subprocess.check_output(['pct','exec','627','--',*a],text=True,timeout=40)
def get(p):return json.load(urllib.request.urlopen('http://192.168.1.127:17493'+p,timeout=15))
def atom(p,data):
 tmp=p.with_suffix('.partial');tmp.write_text(json.dumps(data));tmp.chmod(0o600);os.replace(tmp,p)
def configs():return {p.stem:sha(p) for p in Path('/etc/pve/lxc').glob('*.conf')}
def nojobs(root):
 assert not any(json.loads(p.read_text()).get('status') in ['running','queued'] for p in (root/'srv/voicebox/qwen-worker/jobs').glob('*/state.json'))
 assert not any(n.startswith(('qwen-','chatterbox-','d089-inference-')) for n in ct('docker','ps','--format','{{.Names}}').splitlines())
def app():
 c=json.loads(ct('docker','inspect','voicebox'))[0];assert c['Image']==APP and c['State']['Health']['Status']=='healthy' and c['Config']['User']=='999:999'
 return {'id':c['Id'],'image':c['Image'],'started':c['State']['StartedAt']}
def wait(enabled):
 for _ in range(30):
  caps=get('/tts-capabilities')
  if caps['qwen']['ready'] and caps['chatterbox']['ready']==enabled:return caps
  time.sleep(.5)
 raise RuntimeError('Readiness timeout')
def restore(root):
 state=json.loads((BACK/'state.json').read_text());link=root/'srv/voicebox/qwen-worker/src'
 subprocess.run(['systemctl','stop','voicebox-qwen-627.service'],check=True)
 for n in state.get('controller_files',['readiness.py'])+['chatterbox-release.json']:shutil.copy2(BACK/n,CODE/n)
 tmp=link.with_name('src-d089-rollback');assert not tmp.exists();tmp.symlink_to(state['old_link']);os.replace(tmp,link)
 subprocess.run(['systemctl','start','voicebox-qwen-627.service'],check=True)
 caps=wait(False);assert app()==state['app'];return {'rollback':'PASS','capabilities':caps,'sqlite_restored':False}
def main():
 p=argparse.ArgumentParser();p.add_argument('--action',choices=['deploy','verify','rollback'],required=True);a=p.parse_args()
 pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();root=Path('/proc',pid,'root');base=root/'srv/voicebox/validation-d089';source=base/'integration';lock=json.loads((source/'deployment-lock.json').read_text())
 with open('/run/lock/qwen-d077-627.lock','a') as slot:
  fcntl.flock(slot,fcntl.LOCK_EX|fcntl.LOCK_NB);nojobs(root)
  if a.action=='rollback':print(json.dumps(restore(root)));return
  if a.action=='verify':
   state=json.loads((BACK/'state.json').read_text());assert app()==state['app'] and configs()==state['configs'];assert (root/'srv/voicebox/qwen-worker/src').readlink().as_posix()==state['new_link']
   for n,h in lock['worker'].items():assert sha(root/'srv/voicebox/qwen-worker/src'/n)==h

   for n,h in lock['controller'].items():assert sha(CODE/n)==h
   caps=wait(True)
   print(json.dumps({'idempotent_verification':'PASS','restarts_or_writes':0,'capabilities':caps}));return
  assert not BACK.exists(),'No automatic redeployment'
  assert json.loads((Path('/mnt/storage/d089/backups-verified.json')).read_text())['result']=='PASS'
  r=json.loads((base/'job/supervisor-result.json').read_text());assert r['success'] and r['processes_released'] and r['worker_result']['eos']
  m=r['measurements'];assert max(x.get('worker_current',0) for x in m)<(7*2**30-512*2**20)
  assert max(x.get('worker_swap',0) for x in m)==0 and not any(x.get('worker_events',{}).get('oom',0) for x in m)
  sys.path.insert(0,str(CODE));import supervise,engine_policy
  baseline=supervise.sample();assert engine_policy.preflight(baseline) and get('/health')['status']=='healthy'
  assert int(Path('/sys/fs/cgroup/lxc/627/memory.max').read_text())==20*2**30
  cfg=dict(l.split(': ',1) for l in subprocess.check_output(['pct','config','627'],text=True).splitlines() if ': ' in l)
  assert all(cfg[k]==v for k,v in {'memory':'20480','swap':'2048','cores':'3','rootfs':'local-lvm:vm-627-disk-0,size=100G'}.items())
  pool=subprocess.check_output(['dmsetup','status','/dev/mapper/pve-data-tpool'],text=True).split();used,total=map(int,pool[5].split('/'));assert used/total<.8
  for role in ['worker','controller']:
   for n,h in lock[role].items():assert sha(source/n)==h
  # Exact ML files from the successful isolated run, not a rebuilt approximation.
  for n in lock['worker']:assert sha(source/n)==sha(base/'source'/n)
  release=json.loads((CODE/'chatterbox-release.json').read_text());assert not release['enabled']
  assert release['source_hashes']==lock['original_source_hashes'] and release['worker_hashes']==lock['original_worker_hashes']
  for n,h in release['source_hashes'].items():assert sha(CODE/n)==h
  old=root/'srv/voicebox/qwen-worker/src';assert old.is_symlink()
  for n,h in release['worker_hashes'].items():assert sha(old/n)==h
  original=app();assert get('/tts-capabilities')['qwen']['ready']
  BACK.mkdir(mode=0o700)
  for n in lock['controller']:shutil.copy2(CODE/n,BACK/n)
  shutil.copy2(CODE/'chatterbox-release.json',BACK/'chatterbox-release.json')
  shutil.copytree(CODE,BACK/'controller',ignore=shutil.ignore_patterns('backups','__pycache__','*.pyc'))
  new=old.parent/'src-d089-optimized';assert not new.exists();shutil.copytree(old,new,ignore=shutil.ignore_patterns('__pycache__','*.pyc'))
  for n in lock['worker']:shutil.copy2(source/n,new/n)
  for f in [new,*new.rglob('*')]:os.chown(f,999,999);f.chmod(0o700 if f.is_dir() else 0o600)
  state={'app':original,'old_link':old.readlink().as_posix(),'new_link':new.name,'configs':configs(),'sqlite_restored':False,'controller_files':list(lock['controller'])};atom(BACK/'state.json',state)
  # No schema/database change. Rollback restores only controller code/receipt/src link.
  try:
   nojobs(root);subprocess.run(['systemctl','stop','voicebox-qwen-627.service'],check=True)
   for n in lock['controller']:
    shutil.copy2(source/n,CODE/n);(CODE/n).chmod(0o600)
   pending=old.with_name('src-d089-pending');assert not pending.exists();pending.symlink_to(new.name);os.replace(pending,old)
   release['source_hashes'].update(lock['controller']);release['worker_hashes'].update(lock['worker']);release.update(enabled=True,reason='D089 isolated FP32 inference validated; acoustic acceptance pending')
   atom(CODE/'chatterbox-release.json',release)
   subprocess.run(['systemctl','start','voicebox-qwen-627.service'],check=True)
   caps=wait(True);assert app()==original and configs()==state['configs'];nojobs(root)
   assert caps['qwen']['languages']==caps['chatterbox']['languages']==['es','en'] and caps['qwen']['max_chars']==1200 and caps['chatterbox']['max_chars']==lock['chatterbox_max_chars']
   assert 'baa61a95-c7b4-4524-8229-aa697b941710' in json.dumps(get('/history'))
   result={'deployment':'PASS','app_unchanged':True,'qwen_unchanged':True,'capabilities':caps,'resources_and_configs_unchanged':True,'rollback_ready':True};atom(BACK/'result.json',result);print(json.dumps(result))
  except BaseException as exc:
   rb=restore(root);atom(BACK/'failure.json',{'error':str(exc),'recovery':rb});raise
if __name__=='__main__':main()
