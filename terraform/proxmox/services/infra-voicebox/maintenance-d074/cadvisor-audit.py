"""PVE: read-only CT618 cAdvisor and sibling identity check."""
import json,subprocess,time,datetime
from pathlib import Path

def ct(*args):return subprocess.check_output(['pct','exec','618','--',*args],text=True,timeout=20)
def allmeta():
 ids=ct('docker','ps','-aq').split();rows=json.loads(ct('docker','inspect',*ids))
 return [{'id':x['Id'],'name':x['Name'],'image':x['Image'],'started_at':x['State']['StartedAt'],'status':x['State']['Status'],'restarts':x['RestartCount']} for x in rows]
def cgstat(p):
 r={}
 for k in ['memory.current','memory.max','memory.high','memory.swap.current','memory.swap.max','memory.events','memory.events.local','memory.pressure','memory.stat']:
  r[k]=(p/k).read_text()
 return r
c=json.loads(ct('docker','inspect','cadvisor'))[0];cid=c['Id'];cg=next(Path('/sys/fs/cgroup/lxc/618').rglob('docker-'+cid+'.scope'));before=allmeta();a=cgstat(cg);time.sleep(10);b=cgstat(cg)
r={'at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'container':{'id':cid,'image':c['Image'],'created':c['Created'],'started_at':c['State']['StartedAt'],'restarts':c['RestartCount'],'oom_killed':c['State']['OOMKilled'],'health':c['State'].get('Health',{}).get('Status','not_configured'),'status':c['State']['Status'],'limits':{k:c['HostConfig'][k] for k in ['Memory','MemorySwap','MemoryReservation','NanoCpus']},'compose_config_files':c['Config'].get('Labels',{}).get('com.docker.compose.project.config_files'),'compose_workdir':c['Config'].get('Labels',{}).get('com.docker.compose.project.working_dir')},'before':a,'after':b,'all_containers_before':before,'all_containers_after':allmeta()}
print(json.dumps(r))
