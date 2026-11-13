"""PVE CT627-only D086 coordinated deploy/rollback. Never submits inference."""
from pathlib import Path
import argparse,subprocess,json,hashlib,os,shutil,time,urllib.request,datetime
APP='sha256:19af4754968dacacbb9104f8ea40826dbea4f9f772992397cf322802d7babbfe'
OLD='sha256:09774c5b7c535185c901557ddb6c69a4f8bb38ceff2c6998e19bab403b8e94ea'
CODE=Path('/opt/voicebox-qwen-627');BACK=CODE/'backups/d086-before'

def ct(*a):return subprocess.check_output(['pct','exec','627','--',*a],text=True,timeout=90)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def root():
 pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();r=Path('/proc',pid,'root');assert (r/'etc/hostname').read_text().strip()=='infra-voicebox';return r

def wait_health(expected):
 for _ in range(150):
  try:
   c=json.loads(ct('docker','inspect','voicebox'))[0]
   if c['Image']==expected and c['State']['Health']['Status']=='healthy':return c
  except Exception:pass
  time.sleep(1)
 raise RuntimeError('Voicebox health timeout')

def no_jobs(r):
 jobs=r/'srv/voicebox/qwen-worker/jobs'
 assert not any(json.loads(p.read_text()).get('status') in ['running','queued'] for p in jobs.glob('*/state.json'))
 assert not any(n.startswith(('qwen-','chatterbox-')) for n in ct('docker','ps','--format','{{.Names}}').splitlines())

def rollback(r):
 subprocess.run(['systemctl','stop','voicebox-qwen-627.service'],check=True,capture_output=True)
 state=json.loads((BACK/'state.json').read_text());base=r/'opt/voicebox'
 for n in ['compose.yml','image-lock.json','image-id.txt','deploy.sh']:shutil.copy2(BACK/'operations'/n,base/n)
 for n in state['original_controller_files']:shutil.copy2(BACK/'controller'/n,CODE/n)
 release=CODE/'chatterbox-release.json'
 if release.exists():v=json.loads(release.read_text());v['enabled']=False;release.write_text(json.dumps(v));release.chmod(0o600)
 link=r/'srv/voicebox/qwen-worker/src';tmp=link.with_name('src-rollback-d086');assert not tmp.exists();tmp.symlink_to(state['src_link']);os.replace(tmp,link)
 subprocess.run(['systemctl','start','voicebox-qwen-627.service'],check=True,capture_output=True)
 ct('docker','compose','-f','/opt/voicebox/compose.yml','up','-d','--no-deps','--no-build','--pull','never','voicebox')
 c=wait_health(OLD);return {'rollback':'PASS','image':c['Image'],'healthy':True}

def deploy(r,bundle,release):
 assert not BACK.exists(),'Existing D086 attempt: no automatic redeployment'
 assert subprocess.check_output(['findmnt','-no','SOURCE','/mnt/storage'],text=True).strip()=='/dev/sdb'
 no_jobs(r)
 original=json.loads(ct('docker','inspect','voicebox'))[0];assert original['Image']==OLD and original['State']['Health']['Status']=='healthy'
 assert json.loads(ct('docker','image','inspect','local/voicebox:d085-candidate'))[0]['Id']==APP
 t=subprocess.check_output(['dmsetup','status','/dev/mapper/pve-data-tpool'],text=True).split();u,total=map(int,t[5].split('/'));assert u/total<=.8
 backup=r/'opt/voicebox/backups/d086-before-deploy';assert (backup/'manifest.json').is_file()
 for role,key in [('controller','source_hashes'),('worker','worker_hashes')]:
  for n,h in release[key].items():assert sha(bundle/role/n)==h
 env=r/'srv/voicebox/chatterbox-d085'
 assert sha(env/'models/manifest.json')==release['model_manifest_sha256'] and sha(env/'environment-receipt.json')==release['environment_receipt_sha256']
 m=json.loads((env/'models/manifest.json').read_text())
 for f in m['files']:assert sha(env/'models'/f['name'])==f['sha256']
 BACK.mkdir(mode=0o700,parents=True);(BACK/'operations').mkdir();(BACK/'controller').mkdir()
 base=r/'opt/voicebox'
 for n in ['compose.yml','image-lock.json','image-id.txt','deploy.sh']:shutil.copy2(base/n,BACK/'operations'/n)
 controller=[p.name for p in CODE.glob('*.py')]
 for n in controller:shutil.copy2(CODE/n,BACK/'controller'/n)
 link=r/'srv/voicebox/qwen-worker/src';assert link.is_symlink();old_link=os.readlink(link)
 configs={p.stem:sha(p) for p in Path('/etc/pve/lxc').glob('*.conf')}
 (BACK/'state.json').write_text(json.dumps({'src_link':old_link,'original_controller_files':controller,'configs':configs,'original_image':OLD}));(BACK/'state.json').chmod(0o600)
 (BACK/'runtime.json').write_text(json.dumps({'id':original['Id'],'image':original['Image'],'started_at':original['State']['StartedAt'],'restart_count':original['RestartCount']}))
 (BACK/'627.conf').write_bytes(Path('/etc/pve/lxc/627.conf').read_bytes())
 hdd=Path('/mnt/storage/d086-before-deploy');hdd.mkdir(mode=0o700,exist_ok=False)
 shutil.copy2(backup.with_suffix('.tar.gz'),hdd/'application.tar.gz')
 shutil.copytree(BACK,hdd/'controller')
 # Prepare all target files before pausing the agent; old source tree remains intact.
 digest=hashlib.sha256(json.dumps(release['worker_hashes'],sort_keys=True).encode()).hexdigest()[:16]
 new=link.parent/('src-d086-'+digest);assert not new.exists();shutil.copytree(link,new,ignore=shutil.ignore_patterns('__pycache__'))
 os.chown(new,999,999);new.chmod(0o700)
 for p in (bundle/'worker').iterdir():shutil.copy2(p,new/p.name)
 for p in new.rglob('*'):
  os.chown(p,999,999);p.chmod(0o700 if p.is_dir() else 0o600)
 context=base/'deploy-d086';assert not context.exists();shutil.copytree(bundle,context)
 compose=(base/'compose.yml').read_text();assert compose.count('image: local/voicebox:qwen-isolated-d079')==1
 target=compose.replace('image: local/voicebox:qwen-isolated-d079','image: local/voicebox:d085-candidate').replace('context: ./production-d079','context: ./deploy-d086')
 candidate=base/'compose-d086-check.yml';candidate.write_text(target);candidate.chmod(0o600)
 before_cfg=json.loads(ct('docker','compose','-f','/opt/voicebox/compose.yml','config','--format','json'))
 after_cfg=json.loads(ct('docker','compose','-f','/opt/voicebox/compose-d086-check.yml','config','--format','json'))
 for v in [before_cfg,after_cfg]:
  v['services']['voicebox'].pop('image',None);v['services']['voicebox'].pop('build',None)
 assert before_cfg==after_cfg,'Unexpected change beyond image/build'
 old_lock=json.loads((base/'image-lock.json').read_text());lock=dict(old_lock);lock.update(image='local/voicebox:d085-candidate',image_id=APP,integration='d086-isolated',dockerfile_path='deploy-d086/Dockerfile',dockerfile_sha256=sha(context/'Dockerfile'),overlay='D086 coordinated bilingual Qwen + isolated Chatterbox; acoustic acceptance pending',rollback=old_lock)
 lock['overlay_files']={'deploy-d086/'+str(p.relative_to(context)):sha(p) for p in context.rglob('*') if p.is_file()}
 deployscript=(base/'deploy.sh').read_text();old='("d077-isolated", "d079-isolated")';assert deployscript.count(old)==1;deployscript=deployscript.replace(old,'("d077-isolated", "d079-isolated", "d086-isolated")')
 try:
  no_jobs(r);subprocess.run(['systemctl','stop','voicebox-qwen-627.service'],check=True,capture_output=True)
  for p in (bundle/'controller').iterdir():shutil.copy2(p,CODE/p.name);(CODE/p.name).chmod(0o600)
  tmp=link.with_name('src-pending-d086');assert not tmp.exists();tmp.symlink_to(new.name);os.replace(tmp,link)
  release=dict(release,enabled=True,reason='D086 deployment explicitly authorized; acoustic acceptance pending')
  (CODE/'chatterbox-release.json').write_text(json.dumps(release,indent=2));(CODE/'chatterbox-release.json').chmod(0o600)
  subprocess.run(['systemctl','start','voicebox-qwen-627.service'],check=True,capture_output=True)
  for _ in range(30):
   h=json.loads((link.parent/'jobs/agent-heartbeat.json').read_text())
   if h.get('protocol')=='d083-es-en-v1' and h.get('chatterbox',{}).get('ready') and time.time()-h['timestamp']<8:break
   time.sleep(.5)
  else:raise RuntimeError('Controller or Chatterbox readiness failed')
  (base/'compose.yml').write_text(target);(base/'image-lock.json').write_text(json.dumps(lock,indent=2)+'\n');(base/'image-id.txt').write_text(APP+'\n');(base/'deploy.sh').write_text(deployscript)
  ct('docker','compose','-f','/opt/voicebox/compose.yml','up','-d','--no-deps','--no-build','--pull','never','voicebox')
  c=wait_health(APP)
  caps=json.load(urllib.request.urlopen('http://192.168.1.127:17493/tts-capabilities',timeout=10))
  for e in ['qwen','chatterbox']:assert caps[e]['ready'] and caps[e]['languages']==['es','en']
  assert caps['qwen']['max_chars']==1200 and caps['chatterbox']['max_chars']==240
  assert configs=={p.stem:sha(p) for p in Path('/etc/pve/lxc').glob('*.conf')}
  no_jobs(r)
  return {'deployment':'PASS','image':c['Image'],'container_id':c['Id'],'started_at':c['State']['StartedAt'],'capabilities':caps,'resources_and_ct_configs_unchanged':True,'source_target':new.name,'rollback_ready':True}
 except BaseException as e:
  rb=rollback(r);print(json.dumps({'deployment':'FAILED','error':str(e),'automatic_rollback':rb}),flush=True);raise

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--execute',action='store_true');p.add_argument('--rollback',action='store_true');p.add_argument('--bundle',type=Path);p.add_argument('--release',type=Path);a=p.parse_args();assert a.execute,'Explicit authorized execution required';r=root()
 print(json.dumps(rollback(r) if a.rollback else deploy(r,a.bundle,json.loads(a.release.read_text()))),flush=True)
