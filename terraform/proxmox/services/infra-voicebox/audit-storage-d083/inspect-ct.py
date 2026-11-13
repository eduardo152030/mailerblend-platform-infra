"""Run ONLY in CT627. Read-only disk accounting; no prune, mounts or data changes."""
from pathlib import Path
import subprocess,json,os,socket,datetime
assert socket.gethostname()=='infra-voicebox'
def run(args,timeout=90):
 r=subprocess.run(args,capture_output=True,text=True,timeout=timeout)
 return {'code':r.returncode,'output':r.stdout,'error':r.stderr[:300]}
paths=['/','/var','/var/lib','/var/lib/docker','/var/lib/containerd','/var/log','/opt/voicebox','/opt/voicebox/backups','/srv/voicebox','/srv/voicebox/data','/srv/voicebox/huggingface','/srv/voicebox/qwen-worker','/srv/voicebox/qwen-worker/jobs','/tmp','/var/tmp','/root/.cache','/home/voicebox/.cache']
result={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'df':run(['df','-B1','-T','/']),'usage':{},'permissions':{}}
for path in paths:
 p=Path(path)
 if not p.exists():result['usage'][path]={'absent':True};continue
 result['usage'][path]=run(['nice','-n','19','ionice','-c','3','du','-x','-B1','--max-depth=1',path])
 if path in ['/srv/voicebox','/srv/voicebox/huggingface','/srv/voicebox/data','/srv/voicebox/qwen-worker/jobs']:
  s=p.stat();result['permissions'][path]={'uid':s.st_uid,'gid':s.st_gid,'mode':oct(s.st_mode&0o777),'resolved':str(p.resolve())}
result['docker_info']=run(['docker','info','--format','{{json .DockerRootDir}} {{json .Driver}} {{json .DriverStatus}}'])
result['docker_df']=run(['docker','system','df','--format','{{json .}}'])
result['docker_images']=run(['docker','image','ls','--no-trunc','--format','{{json .}}'])
result['container_rw']=run(['docker','inspect','--size','--format','{{.Name}} {{.SizeRw}} {{.SizeRootFs}}',*subprocess.check_output(['docker','ps','-aq'],text=True).split()])
c=json.loads(subprocess.check_output(['docker','inspect','voicebox']))[0]
result['voicebox']={'image':c['Image'],'id':c['Id'],'started_at':c['State']['StartedAt'],'health':c['State']['Health']['Status'],'mounts':c['Mounts'],'paths_env':{x.split('=',1)[0]:x.split('=',1)[1] for x in c['Config']['Env'] if x.split('=',1)[0] in ['HF_HOME','HUGGINGFACE_HUB_CACHE','TRANSFORMERS_CACHE','XDG_CACHE_HOME','TMPDIR','HF_HUB_OFFLINE']}}
volumes=subprocess.check_output(['docker','volume','ls','-q'],text=True).split();result['docker_volume_mounts']=[]
for name in volumes:
 v=json.loads(subprocess.check_output(['docker','volume','inspect',name]))[0];result['docker_volume_mounts'].append({'name':name,'mountpoint':v['Mountpoint']})
result['mounts']=run(['findmnt','--json','-o','TARGET,SOURCE,FSTYPE,OPTIONS'])
print(json.dumps(result))
