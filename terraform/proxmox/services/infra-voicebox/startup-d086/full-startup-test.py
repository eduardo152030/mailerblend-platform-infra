"""PVE: real entrypoint/CMD, production configuration with isolated bind copies.
Never publishes ports, touches production data, changes controller or invokes TTS.
"""
import subprocess,json,time,datetime,os
from pathlib import Path
ROOT='/srv/voicebox/chatterbox-d085/startup-validation';NAME='voicebox-d086-startup-test'
def ct(*a):return subprocess.check_output(['pct','exec','627','--',*a],text=True,timeout=60)
def main():
 pid=subprocess.check_output(['lxc-info','-n','627','-pH'],text=True).strip();root=Path('/proc',pid,'root');fixture=root/ROOT.lstrip('/');assert fixture.is_dir()
 before=json.loads(ct('docker','inspect','voicebox'))[0];assert before['State']['Health']['Status']=='healthy'
 image=json.loads(ct('docker','image','inspect','local/voicebox:d086-uid999-candidate'))[0];bad=json.loads(ct('docker','image','inspect','local/voicebox:d085-candidate'))[0]
 assert image['Config']['User']=='999:999' and image['Config']['Cmd']==bad['Config']['Cmd']
 assert image['Config']['Env']==bad['Config']['Env'] and image['Config']['WorkingDir']==bad['Config']['WorkingDir']
 cfg=json.loads(ct('docker','compose','-f','/opt/voicebox/compose.yml','config','--format','json'));service=cfg['services']['voicebox']
 service['image']='local/voicebox:d086-uid999-candidate';service.pop('build',None);service['container_name']=NAME;service['restart']='no';service.pop('ports',None);service.pop('networks',None);service['network_mode']='none'
 assert not service.get('entrypoint') and not service.get('command') and not service.get('user')
 mapping={'/srv/voicebox/data':ROOT+'/data','/srv/voicebox/huggingface':ROOT+'/huggingface','/srv/voicebox/qwen-worker/jobs':ROOT+'/jobs'}
 for volume in service['volumes']:assert volume['source'] in mapping;volume['source']=mapping[volume['source']]
 doc={'name':'voicebox-d086-isolated-startup','services':{'voicebox':service}}
 compose=fixture/'compose.json';compose.write_text(json.dumps(doc,indent=2));compose.chmod(0o600)
 result={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'image_id':image['Id'],'user':image['Config']['User'],'entrypoint':image['Config']['Entrypoint'],'cmd':image['Config']['Cmd'],'same_app_environment':True,'real_entrypoint_used':True,'ports_published':False,'bind_sources_private_copies':True}
 started=False
 try:
  ct('docker','compose','-f',ROOT+'/compose.json','up','-d','--no-build','--pull','never','voicebox');started=True
  for _ in range(180):
   state=json.loads(ct('docker','inspect',NAME))[0]
   if not state['State']['Running']:raise RuntimeError('Real entrypoint exited: inspect private test log')
   if state['State'].get('Health',{}).get('Status')=='unhealthy':raise RuntimeError('Startup unhealthy')
   if state['State'].get('Health',{}).get('Status')=='healthy':break
   time.sleep(1)
  else:raise TimeoutError('Real startup did not reach healthy')
  for k in ['Memory','MemorySwap','NanoCpus','Privileged','CapAdd','CapDrop','SecurityOpt','ReadonlyRootfs','PidsLimit','UsernsMode']:
   assert state['HostConfig'].get(k)==before['HostConfig'].get(k),k
  assert not state['NetworkSettings']['Ports'] and state['HostConfig']['NetworkMode']=='none'
  assert dict(v.split('=',1) for v in state['Config']['Env'])==dict(v.split('=',1) for v in before['Config']['Env']),'Unexpected app environment drift'
  audit="""import os,json,sqlite3,urllib.request,importlib.util
from pathlib import Path
assert os.geteuid()==999 and os.getegid()==999
status=dict(x.split(':',1) for x in Path('/proc/1/status').read_text().splitlines() if ':' in x)
assert status['Uid'].split()==['999']*4 and int(status['CapEff'].strip(),16)==0 and int(status['CapPrm'].strip(),16)==0
for module in ['backend.config','backend.models','backend.routes.generations','backend.backends.isolated_backend','backend.backends.isolated_chatterbox_backend']:assert importlib.util.find_spec(module)
checks={}
for name in ['/app/data','/app/data/cache','/app/data/cache/numba','/app/data/profiles','/app/data/generations','/qwen-jobs','/home/voicebox/.cache','/home/voicebox/.cache/huggingface']:
 p=Path(name);assert os.access(p,os.R_OK|os.W_OK|os.X_OK);probe=p/'.d086-startup-access-probe';assert not probe.exists();probe.write_text('isolated fixture only');assert probe.stat().st_uid==999;probe.unlink();checks[name]=True
db=sqlite3.connect('/app/data/voicebox.db');assert db.execute('pragma integrity_check').fetchone()[0]=='ok';db.execute('BEGIN');db.execute('CREATE TABLE d086_write_probe (value TEXT)');db.execute('INSERT INTO d086_write_probe VALUES (?)',('probe',));db.rollback();assert db.execute(\"select count(*) from sqlite_master where name='d086_write_probe'\").fetchone()[0]==0
counts={t:db.execute('select count(*) from '+t).fetchone()[0] for t in ['profiles','profile_samples','generations']};db.close()
with urllib.request.urlopen('http://127.0.0.1:17493/health',timeout=5) as f:health=json.load(f)
assert health['status']=='healthy' and not health['model_loaded']
print(json.dumps({'uid':os.geteuid(),'gid':os.getegid(),'pid1_uid':status['Uid'].strip(),'cap_eff':status['CapEff'].strip(),'cap_prm':status['CapPrm'].strip(),'cache_owner':Path('/home/voicebox/.cache').stat().st_uid,'module_access':True,'directory_access':checks,'sqlite_integrity':'ok','sqlite_read_write_rollback':True,'database_counts':counts,'model_loaded':False,'healthy':True}))"""
  result['audit']=json.loads(ct('docker','exec',NAME,'python','-c',audit));result['result']='PASS'
  (fixture/'startup-result.json').write_text(json.dumps(result,indent=2))
  return result
 finally:
  if started:
   log=subprocess.run(['pct','exec','627','--','docker','logs',NAME],capture_output=True,text=True);(fixture/'startup.private.log').write_text(log.stdout+log.stderr);(fixture/'startup.private.log').chmod(0o600)
   subprocess.run(['pct','exec','627','--','docker','stop','--time','10',NAME],capture_output=True,timeout=30)
   final=json.loads(ct('docker','inspect',NAME))[0];assert not final['State']['Running'] and final['State']['Pid']==0
   result['test_processes_released']=True
  current=json.loads(ct('docker','inspect','voicebox'))[0];assert current['Id']==before['Id'] and current['State']['StartedAt']==before['State']['StartedAt'] and current['State']['Health']['Status']=='healthy'
  result['production_same_id_and_started_at']=True
if __name__=='__main__':print(json.dumps(main()))
