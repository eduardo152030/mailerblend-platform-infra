"""PVE CT627-only D087 coordinated deploy/rollback. Never submits inference."""
from pathlib import Path
import argparse,subprocess,json,hashlib,os,shutil,time,urllib.request,datetime,sys,re
sys.dont_write_bytecode=True
APP='sha256:212703647c03d428adc30f8bf4b864af82690eb41f4fe8ca052ff10dbaa45386'
OLD='sha256:09774c5b7c535185c901557ddb6c69a4f8bb38ceff2c6998e19bab403b8e94ea'
CODE=Path('/opt/voicebox-qwen-627');ATTEMPT='d087';BACK=CODE/('backups/'+ATTEMPT+'-before')

def ct(*a):return subprocess.check_output(['pct','exec','627','--',*a],text=True,timeout=90)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def copy_locked(source,target,hashes):
 """Copy only declared, verified Python files; ignore generated cache directories."""
 for name,expected in hashes.items():
  assert Path(name).name==name and name.endswith('.py'),'Unsafe locked source name'
  p=source/name
  assert p.is_file() and not p.is_symlink() and sha(p)==expected,'Locked source mismatch'
 for name in hashes:
  shutil.copy2(source/name,target/name);(target/name).chmod(0o600)

def root():
 pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();r=Path('/proc',pid,'root');assert (r/'etc/hostname').read_text().strip()=='infra-voicebox';return r

def wait_health(expected):
 for _ in range(150):
  try:
   c=json.loads(ct('docker','inspect','voicebox'))[0]
   if c['Image']==expected and c['State']['Health']['Status']=='healthy':return c
   if c['Image']==expected and (c['State'].get('Health',{}).get('Status')=='unhealthy' or c['RestartCount']>0):raise RuntimeError('Critical startup failure')
  except RuntimeError:raise
  except Exception:pass
  time.sleep(1)
 raise RuntimeError('Voicebox health timeout')

def no_jobs(r):
 jobs=r/'srv/voicebox/qwen-worker/jobs'
 assert not any(json.loads(p.read_text()).get('status') in ['running','queued'] for p in jobs.glob('*/state.json'))
 assert not any(n.startswith(('qwen-','chatterbox-')) for n in ct('docker','ps','--format','{{.Names}}').splitlines())

def resource_preflight(bundle):
 # Pure policy imports only; never load a model. Include all CT file/kernel pages.
 sys.path.insert(0,str(bundle/'controller'))
 from engine_policy import preflight as chatterbox_preflight
 from guards import predictive_preflight
 cg=Path('/sys/fs/cgroup/lxc/627')
 cfg=dict(line.split(': ',1) for line in subprocess.check_output(['pct','config','627'],text=True).splitlines() if ': ' in line)
 assert cfg['memory']=='20480' and cfg['cores']=='3' and cfg['swap']=='2048' and cfg['rootfs']=='local-lvm:vm-627-disk-0,size=100G'
 assert int((cg/'memory.max').read_text())==20*2**30 and int((cg/'memory.swap.max').read_text())==2*2**30
 available=int(next(l.split()[1] for l in Path('/proc/meminfo').read_text().splitlines() if l.startswith('MemAvailable:')))*1024
 full=next(l for l in (cg/'memory.pressure').read_text().splitlines() if l.startswith('full '))
 sample={'ct_current':int((cg/'memory.current').read_text()),'host_available':available,
         'ct_psi_full_avg10':float(full.split('avg10=')[1].split()[0]),'ct_swap':int((cg/'memory.swap.current').read_text())}
 assert available>=12*2**30,'Host MemAvailable below existing Qwen preflight minimum'
 assert predictive_preflight(sample)['passed'],'Qwen predictive preflight failed; production unchanged'
 assert chatterbox_preflight(sample),'Chatterbox predictive preflight failed; production unchanged'
 return sample

def rollback(r):
 subprocess.run(['systemctl','stop','voicebox-qwen-627.service'],check=True,capture_output=True)
 state=json.loads((BACK/'state.json').read_text());base=r/'opt/voicebox'
 for n in ['compose.yml','image-lock.json','image-id.txt','deploy.sh']:shutil.copy2(BACK/'operations'/n,base/n)
 for n in state['original_controller_files']:shutil.copy2(BACK/'controller'/n,CODE/n)
 release=CODE/'chatterbox-release.json'
 if release.exists():v=json.loads(release.read_text());v['enabled']=False;release.write_text(json.dumps(v));release.chmod(0o600)
 link=r/'srv/voicebox/qwen-worker/src';tmp=link.with_name(('src-rollback-'+ATTEMPT));assert not tmp.exists();tmp.symlink_to(state['src_link']);os.replace(tmp,link)
 subprocess.run(['systemctl','start','voicebox-qwen-627.service'],check=True,capture_output=True)
 ct('docker','compose','-f','/opt/voicebox/compose.yml','up','-d','--no-deps','--no-build','--pull','never','voicebox')
 c=wait_health(OLD);return {'rollback':'PASS','image':c['Image'],'healthy':True}

def deploy(r,bundle,release):
 assert not BACK.exists(),'Existing D087 attempt: no automatic redeployment'
 assert subprocess.check_output(['findmnt','-no','SOURCE','/mnt/storage'],text=True).strip()=='/dev/sdb'
 no_jobs(r)
 sys.path.insert(0,str(CODE))
 resource_preflight(bundle)
 original=json.loads(ct('docker','inspect','voicebox'))[0];assert original['Image']==OLD and original['State']['Health']['Status']=='healthy'
 image=json.loads(ct('docker','image','inspect','local/voicebox:d086-uid999-candidate'))[0]
 assert image['Id']==APP and image['Config']['User']=='999:999'
 assert image['Config']['Entrypoint']==['/usr/local/bin/entrypoint-uid999.sh']
 assert image['Config']['Cmd']==['uvicorn','backend.main:app','--host','0.0.0.0','--port','17493']
 t=subprocess.check_output(['dmsetup','status','/dev/mapper/pve-data-tpool'],text=True).split();u,total=map(int,t[5].split('/'));assert u/total<=.8
 backup=r/('opt/voicebox/backups/'+ATTEMPT+'-before-deploy');assert (backup/'manifest.json').is_file()
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
 hdd=Path('/mnt/storage')/(ATTEMPT+'-before-deploy');hdd.mkdir(mode=0o700,exist_ok=False)
 shutil.copy2(backup.with_suffix('.tar.gz'),hdd/'application.tar.gz')
 shutil.copytree(BACK,hdd/'controller')
 # Prepare all target files before pausing the agent; old source tree remains intact.
 digest=hashlib.sha256(json.dumps(release['worker_hashes'],sort_keys=True).encode()).hexdigest()[:16]
 new=link.parent/('src-'+ATTEMPT+'-'+digest);assert not new.exists();shutil.copytree(link,new,ignore=shutil.ignore_patterns('__pycache__'))
 os.chown(new,999,999);new.chmod(0o700)
 copy_locked(bundle/'worker',new,release['worker_hashes'])
 for p in new.rglob('*'):
  os.chown(p,999,999);p.chmod(0o700 if p.is_dir() else 0o600)
 context=base/('deploy-'+ATTEMPT);assert not context.exists();shutil.copytree(bundle,context,ignore=shutil.ignore_patterns("__pycache__","*.pyc"))
 compose=(base/'compose.yml').read_text();assert compose.count('image: local/voicebox:qwen-isolated-d079')==1
 target=compose.replace('image: local/voicebox:qwen-isolated-d079','image: local/voicebox:d086-uid999-candidate').replace('context: ./production-d079',('context: ./deploy-'+ATTEMPT))
 candidate=base/('compose-'+ATTEMPT+'-check.yml');candidate.write_text(target);candidate.chmod(0o600)
 before_cfg=json.loads(ct('docker','compose','-f','/opt/voicebox/compose.yml','config','--format','json'))
 after_cfg=json.loads(ct('docker','compose','-f',('/opt/voicebox/compose-'+ATTEMPT+'-check.yml'),'config','--format','json'))
 for v in [before_cfg,after_cfg]:
  v['services']['voicebox'].pop('image',None);v['services']['voicebox'].pop('build',None)
 assert before_cfg==after_cfg,'Unexpected change beyond image/build'
 old_lock=json.loads((base/'image-lock.json').read_text());lock=dict(old_lock);lock.update(image='local/voicebox:d086-uid999-candidate',image_id=APP,integration=ATTEMPT+'-isolated',dockerfile_path='deploy-'+ATTEMPT+'/Dockerfile',dockerfile_sha256=sha(context/'Dockerfile'),overlay='D087 coordinated bilingual Qwen + isolated Chatterbox; acoustic acceptance pending',rollback=old_lock)
 lock['overlay_files']={'deploy-'+ATTEMPT+'/'+str(p.relative_to(context)):sha(p) for p in context.rglob('*') if p.is_file()}
 deployscript=(base/'deploy.sh').read_text();old='("d077-isolated", "d079-isolated")';assert deployscript.count(old)==1;deployscript=deployscript.replace(old,'("d077-isolated", "d079-isolated", "'+ATTEMPT+'-isolated")')
 try:
  no_jobs(r);subprocess.run(['systemctl','stop','voicebox-qwen-627.service'],check=True,capture_output=True)
  copy_locked(bundle/'controller',CODE,release['source_hashes'])
  tmp=link.with_name(('src-pending-'+ATTEMPT));assert not tmp.exists();tmp.symlink_to(new.name);os.replace(tmp,link)
  release=dict(release,enabled=True,reason='D087 deployment explicitly authorized; acoustic acceptance pending')
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
  assert c['Config']['User']=='999:999' and not c['HostConfig']['Privileged'] and not c['HostConfig']['CapAdd']
  assert c['Config']['Entrypoint']==['/usr/local/bin/entrypoint-uid999.sh']
  status=ct('docker','exec','voicebox','cat','/proc/1/status')
  fields=dict(line.split(':',1) for line in status.splitlines() if ':' in line)
  assert fields['Uid'].split()==['999']*4 and fields['Gid'].split()==['999']*4
  assert int(fields['CapEff'],16)==0 and int(fields['CapPrm'],16)==0
  caps=json.load(urllib.request.urlopen('http://192.168.1.127:17493/tts-capabilities',timeout=10))
  for e in ['qwen','chatterbox']:assert caps[e]['ready'] and caps[e]['languages']==['es','en']
  assert caps['qwen']['max_chars']==1200 and caps['chatterbox']['max_chars']==release['max_chars']
  assert configs=={p.stem:sha(p) for p in Path('/etc/pve/lxc').glob('*.conf')}
  no_jobs(r)
  ct('python3',('/opt/voicebox/deploy-'+ATTEMPT+'/verify-data.py'),'--baseline','/opt/voicebox/backups/'+ATTEMPT+'-before-deploy')
  return {'deployment':'PASS','image':c['Image'],'container_id':c['Id'],'started_at':c['State']['StartedAt'],'capabilities':caps,'resources_and_ct_configs_unchanged':True,'source_target':new.name,'rollback_ready':True}
 except BaseException as e:
  rb=rollback(r);print(json.dumps({'deployment':'FAILED','error':str(e),'automatic_rollback':rb}),flush=True);raise

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--attempt',default='d087');p.add_argument('--execute',action='store_true');p.add_argument('--rollback',action='store_true');p.add_argument('--bundle',type=Path);p.add_argument('--release',type=Path);a=p.parse_args();assert a.execute,'Explicit authorized execution required';assert re.fullmatch(r'd087[a-z]?',a.attempt),'Invalid attempt';ATTEMPT=a.attempt;BACK=CODE/('backups/'+ATTEMPT+'-before');r=root()
 print(json.dumps(rollback(r) if a.rollback else deploy(r,a.bundle,json.loads(a.release.read_text()))),flush=True)
