"""PVE CT627-only coordinated input-limit deploy. No inference; automatic rollback."""
from pathlib import Path
import argparse,fcntl,hashlib,json,os,re,shutil,subprocess,sys,time,urllib.request
sys.dont_write_bytecode=True
BASE='/srv/voicebox/input1200-deploy/context';CODE=Path('/opt/voicebox-qwen-627');BACK=Path('/mnt/storage/input1200-deploy/control-backup-r2')
OLD='sha256:212703647c03d428adc30f8bf4b864af82690eb41f4fe8ca052ff10dbaa45386';TAG='local/voicebox:input1200-3987cab';URL='http://192.168.1.127:17493'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def ct(*a):return subprocess.check_output(['pct','exec','627','--',*a],text=True,timeout=90)
def get(p):return json.load(urllib.request.urlopen(URL+p,timeout=20))
def atom(p,d):
 tmp=p.with_suffix('.partial');tmp.write_text(json.dumps(d,indent=2));tmp.chmod(0o600)
 with tmp.open('rb') as f:os.fsync(f.fileno())
 os.replace(tmp,p)
def configs():return {p.stem:sha(p) for p in Path('/etc/pve/lxc').glob('*.conf')}
def nojobs(r):
 assert not any(json.loads(p.read_text()).get('status') in ['running','queued'] for p in (r/'srv/voicebox/qwen-worker/jobs').glob('*/state.json')),'Job active: do not restart'
 assert not any(n.startswith(('qwen-','chatterbox-','d089-inference-')) for n in ct('docker','ps','--format','{{.Names}}').splitlines())
def wait(expected):
 for _ in range(90):
  c=json.loads(ct('docker','inspect','voicebox'))[0]
  if c['Image']==expected and c['State'].get('Health',{}).get('Status')=='healthy':return c
  if c['RestartCount'] or c['State'].get('Health',{}).get('Status')=='unhealthy':raise RuntimeError('Unstable app startup')
  time.sleep(1)
 raise RuntimeError('App startup timeout')
def validate(r,expected,state):
 c=wait(expected);assert c['Config']['User']=='999:999' and not c['HostConfig']['Privileged'] and not c['HostConfig']['CapAdd']
 status=dict(l.split(':',1) for l in ct('docker','exec','voicebox','cat','/proc/1/status').splitlines() if ':' in l)
 assert status['Uid'].split()==['999']*4 and status['Gid'].split()==['999']*4 and int(status['CapEff'],16)==0
 assert get('/health')['status']=='healthy' and not get('/health')['model_loaded']
 caps=get('/tts-capabilities')
 for engine in ['qwen','chatterbox']:assert caps[engine]['ready'] and caps[engine]['languages']==['es','en'] and caps[engine]['max_chars']==1200
 assert caps['kokoro']['ready'] and caps['piper']['ready']
 jobs=r/'srv/voicebox/qwen-worker/jobs';h=json.loads((jobs/'agent-heartbeat.json').read_text());assert h['status']=='healthy' and time.time()-h['timestamp']<8 and h['chatterbox']['ready']
 release=json.loads((CODE/'chatterbox-release.json').read_text())
 for folder,key in [(CODE,'source_hashes'),(jobs.parent/'src','worker_hashes')]:
  for n,d in release[key].items():assert sha(folder/n)==d
 assert sha(CODE/'engine_policy.py')==state['target_policy_sha256'] and sha(jobs.parent/'src/engine_policy.py')==state['target_policy_sha256']
 assert sha(jobs.parent/'src/worker.py')==state['qwen_worker_sha256']
 assert sha(jobs.parent/'src/chatterbox_worker.py')==state['cb_worker_sha256']
 assert hashlib.sha256(json.dumps(get('/effects/presets'),sort_keys=True).encode()).hexdigest()==state['effects_sha256']
 # Real served UI, not merely a source file: find the imported entry bundle and its limit constant.
 index=urllib.request.urlopen(URL+'/',timeout=20).read().decode();assets=re.findall(r'(?:/|\./)assets/([^" ]+\.js)',index);assert assets
 bundles=[]
 for name in assets:
  data=urllib.request.urlopen(URL+'/assets/'+name,timeout=20).read();assert hashlib.sha256(data).hexdigest()==state['frontend_hashes']['assets/'+name];s=data.decode();bundles.append(s)
 # Verify the function actually retained by minification, not an unused description.
 matched=False
 for s in bundles:
  match=re.search(r'return ([A-Za-z_$][\w$]*)==="chatterbox"\?([A-Za-z_$][\w$]*|1200):\1==="qwen"\?1200',s)
  if match:
   value=match.group(2)
   matched=(value=='1200' or re.search(r'\b'+re.escape(value)+r'=1200(?:[,;])',s) is not None) and 'Audio effects' in s
   if matched:break
 assert matched,'Served UI input policy not verified'

 api=ct('docker','exec','voicebox','python','-c',"from pathlib import Path;print(Path('/app/backend/backends/engine_policy.py').read_text())")
 assert 'CHATTERBOX_MAX_CHARS = 1200' in api and "'max_chars':CB['max_chars']" in api
 for ident in ['baa61a95-c7b4-4524-8229-aa697b941710','9a8ba53a-6032-4ab0-bfa6-8521e4d1de77','bde1cb38-1cc7-4d37-a77e-6226bd0762b3','27af4ddc-c17a-4e10-9dc2-b3fe2d569329']:
  with urllib.request.urlopen(URL+'/audio/'+ident,timeout=20) as response:assert response.status==200 and response.read(12)[:4]==b'RIFF'
 assert 'baa61a95-c7b4-4524-8229-aa697b941710' in json.dumps(get('/history'))
 assert configs()==state['configs'];assert subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip()==state['ct_pid']
 events={k:int(v) for k,v in (l.split() for l in Path('/sys/fs/cgroup/lxc/627/memory.events').read_text().splitlines())}
 for k in ['oom','oom_kill']:assert events[k]==state['ct_events'][k]
 nojobs(r)
 return {'healthy':True,'image_id':c['Image'],'container_id':c['Id'],'started_at':c['State']['StartedAt'],'uid':999,'cap_eff':0,'capabilities':caps,'frontend_sha256':state['frontend_hashes'],'old_wavs_accessible':True,'effects_preserved':True,'qwen_worker_unchanged':True,'cb_generation_worker_unchanged':True,'ct_configs_and_pid_unchanged':True,'no_new_oom':True,'no_active_inference':True}
def rollback(r):
 state=json.loads((BACK/'state.json').read_text());nojobs(r)
 subprocess.run(['systemctl','stop','voicebox-qwen-627.service'],check=True,capture_output=True)
 for n in ['compose.yml','image-lock.json','image-id.txt','deploy.sh']:shutil.copy2(BACK/'operations'/n,r/'opt/voicebox'/n)
 for n in ['engine_policy.py','chatterbox-release.json']:shutil.copy2(BACK/n,CODE/n)
 link=r/'srv/voicebox/qwen-worker/src';tmp=link.with_name('src-input1200-rollback');assert not tmp.exists();tmp.symlink_to(state['old_link']);os.replace(tmp,link)
 subprocess.run(['systemctl','start','voicebox-qwen-627.service'],check=True,capture_output=True)
 ct('docker','compose','-f','/opt/voicebox/compose.yml','up','-d','--no-deps','--no-build','--pull','never','voicebox');wait(OLD)
 for _ in range(30):
  caps=get('/tts-capabilities')
  if caps['qwen']['ready'] and caps['chatterbox']['ready'] and caps['chatterbox']['max_chars']==240:break
  time.sleep(.5)
 else:raise RuntimeError('Rollback readiness not confirmed')
 result={'rollback':'PASS','image_id':OLD,'qwen_ready':True,'chatterbox_max_chars':240,'sqlite_restored':False};atom(BACK/'rollback-result.json',result);return result
def main():
 p=argparse.ArgumentParser();p.add_argument('--action',choices=['deploy','verify','rollback'],required=True);a=p.parse_args()
 pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();r=Path('/proc',pid,'root');context=r/BASE.lstrip('/');base=r/'opt/voicebox';link=r/'srv/voicebox/qwen-worker/src'
 with open('/run/lock/qwen-d077-627.lock','a') as lock:
  fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB);nojobs(r)
  if a.action=='rollback':print(json.dumps(rollback(r)));return
  image=json.loads(Path('/mnt/storage/input1200-deploy/image.json').read_text());target=image['image_id']
  if BACK.exists():
   assert (BACK/'result.json').is_file(),'Previous attempt incomplete: no blind retry'
   state=json.loads((BACK/'state.json').read_text());v=validate(r,target,state);print(json.dumps({'idempotent':'PASS','writes_or_restarts':0,**v}));return
  assert a.action=='deploy'
  assert json.loads(Path('/mnt/storage/input1200-deploy/backup-verified.json').read_text())['result']=='PASS'
  manifest=json.loads((context/'context-manifest.json').read_text())
  for n,h in manifest['files'].items():assert sha(context/n)==h
  current=json.loads(ct('docker','inspect','voicebox'))[0];assert current['Image']==OLD and current['State']['Health']['Status']=='healthy'
  cg=Path('/sys/fs/cgroup/lxc/627');cfg=dict(l.split(': ',1) for l in subprocess.check_output(['pct','config','627'],text=True).splitlines() if ': ' in l)
  assert all(cfg[k]==v for k,v in {'memory':'20480','cores':'3','swap':'2048','rootfs':'local-lvm:vm-627-disk-0,size=100G'}.items())
  sys.path.insert(0,str(CODE));import supervise,engine_policy
  sample=supervise.sample();assert engine_policy.preflight(sample) and sample['host_available']>=12*2**30
  pool=subprocess.check_output(['dmsetup','status','/dev/mapper/pve-data-tpool'],text=True).split();used,total=map(int,pool[5].split('/'));assert used/total<.8
  assert int(cg.joinpath('memory.max').read_text())==20*2**30
  assert engine_policy.CB['max_tokens']==400 and engine_policy.CB['timeout_seconds']==300 and engine_policy.CB['worker_stop_bytes']==7*2**30 and engine_policy.CB['worker_hard_bytes']==8*2**30
  assert get('/health')['status']=='healthy' and not get('/health')['model_loaded']
  oldrelease=json.loads((CODE/'chatterbox-release.json').read_text());assert oldrelease['enabled']
  for folder,key in [(CODE,'source_hashes'),(link,'worker_hashes')]:
   for n,h in oldrelease[key].items():assert sha(folder/n)==h
  BACK.mkdir(mode=0o700);(BACK/'operations').mkdir()
  for n in ['compose.yml','image-lock.json','image-id.txt','deploy.sh']:shutil.copy2(base/n,BACK/'operations'/n)
  for n in ['engine_policy.py','chatterbox-release.json']:shutil.copy2(CODE/n,BACK/n)
  shutil.copytree(CODE,BACK/'controller',ignore=shutil.ignore_patterns('backups','__pycache__','*.pyc'))
  policy_sha=sha(context/'controller-engine_policy.py');new=link.parent/'src-input1200-3987cab-r2';assert not new.exists();shutil.copytree(link,new,ignore=shutil.ignore_patterns('__pycache__','*.pyc'));shutil.copy2(context/'controller-engine_policy.py',new/'engine_policy.py')
  for f in [new,*new.rglob('*')]:os.chown(f,999,999);f.chmod(0o700 if f.is_dir() else 0o600)
  deployment=base/'deploy-input1200-r2';assert not deployment.exists();shutil.copytree(context,deployment)
  compose=(base/'compose.yml').read_text();assert compose.count('image: local/voicebox:d086-uid999-candidate')==1 and compose.count('context: ./deploy-d087b')==1
  compose=compose.replace('image: local/voicebox:d086-uid999-candidate','image: '+TAG).replace('context: ./deploy-d087b','context: ./deploy-input1200-r2')
  check=base/'compose-input1200-r2-check.yml';check.write_text(compose);check.chmod(0o600)
  before_cfg=json.loads(ct('docker','compose','-f','/opt/voicebox/compose.yml','config','--format','json'));after_cfg=json.loads(ct('docker','compose','-f','/opt/voicebox/compose-input1200-r2-check.yml','config','--format','json'))
  for d in [before_cfg,after_cfg]:d['services']['voicebox'].pop('image',None);d['services']['voicebox'].pop('build',None)
  assert before_cfg==after_cfg,'Compose drift beyond image/build'
  state={'configs':configs(),'ct_pid':pid,'ct_events':sample['ct_events'],'old_link':link.readlink().as_posix(),'target_policy_sha256':policy_sha,'qwen_worker_sha256':sha(link/'worker.py'),'cb_worker_sha256':sha(link/'chatterbox_worker.py'),'effects_sha256':hashlib.sha256(json.dumps(get('/effects/presets'),sort_keys=True).encode()).hexdigest(),'frontend_hashes':{n.removeprefix('frontend/'):h for n,h in manifest['files'].items() if n.startswith('frontend/')}};atom(BACK/'state.json',state)
  oldlock=json.loads((base/'image-lock.json').read_text());newlock=dict(oldlock)
  for n in ['archive_sha256','archive_bytes','archive_includes_image_ids']:newlock.pop(n,None)
  newlock.update(image=TAG,image_id=target,integration='input1200-isolated',git_revision=manifest['source_commit'],base_image_id=OLD,dockerfile_path='deploy-input1200-r2/Dockerfile',dockerfile_sha256=sha(deployment/'Dockerfile'),overlay='Input admission1200 only; full narration unvalidated',overlay_files={'deploy-input1200-r2/'+str(p.relative_to(deployment)):sha(p) for p in deployment.rglob('*') if p.is_file()},archive_status='Prior image/archive preserved in rollback; new image rebuilt from verified base and pinned frontend source',rollback=oldlock)
  script=(base/'deploy.sh').read_text();needle='("d077-isolated", "d079-isolated", "d087b-isolated")';assert script.count(needle)==1;script=script.replace(needle,'("d077-isolated", "d079-isolated", "d087b-isolated", "input1200-isolated")')
  try:
   nojobs(r);subprocess.run(['systemctl','stop','voicebox-qwen-627.service'],check=True,capture_output=True);nojobs(r)
   shutil.copy2(context/'controller-engine_policy.py',CODE/'engine_policy.py');(CODE/'engine_policy.py').chmod(0o600)
   tmp=link.with_name('src-input1200-pending');assert not tmp.exists();tmp.symlink_to(new.name);os.replace(tmp,link)
   release=dict(oldrelease);release['source_hashes']['engine_policy.py']=policy_sha;release['worker_hashes']['engine_policy.py']=policy_sha;release.update(max_chars=1200,reason='Input1200 deployment authorized; complete long narration unvalidated');atom(CODE/'chatterbox-release.json',release)
   (base/'compose.yml').write_text(compose);atom(base/'image-lock.json',newlock);(base/'image-id.txt').write_text(target+'\n');(base/'deploy.sh').write_text(script)
   subprocess.run(['systemctl','start','voicebox-qwen-627.service'],check=True,capture_output=True)
   ct('docker','compose','-f','/opt/voicebox/compose.yml','up','-d','--no-deps','--no-build','--pull','never','voicebox')
   result=validate(r,target,state);atom(BACK/'result.json',result);print(json.dumps({'deployment':'PASS',**result}))
  except BaseException as exc:
   rb=rollback(r);atom(BACK/'failure.json',{'error':str(exc),'rollback':rb});raise
if __name__=='__main__':main()
