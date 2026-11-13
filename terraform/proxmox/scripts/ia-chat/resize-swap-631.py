#!/usr/bin/env python3
"""Swap631 desde YAML; API PVE con digest, backup e idempotencia, sin reinicios."""
import argparse,json,subprocess,shlex,yaml
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--apply',action='store_true');p.add_argument('--label',default='before');a=p.parse_args();assert a.label.replace('-','').isalnum()
d=yaml.safe_load((ROOT/'inventory/services/infra-webui.yml').read_text());assert d['service']['vmid']==631 and d['resources']['swap']==1741
payload={'apply':a.apply,'swap':d['resources']['swap']}
code=r'''
import json,subprocess,sys,pathlib,hashlib,datetime,urllib.request
args=json.load(sys.stdin);path='/nodes/pve/lxc/631/config'
def run(*a):return subprocess.check_output(a,text=True).strip()
def config():return json.loads(run('pvesh','get',path,'--output-format','json'))
def protected():return {p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in pathlib.Path('/etc/pve/lxc').glob('*.conf') if p.stem!='631'}
def identities():return run('pct','exec','631','--','docker','inspect','--format','{{.Name}}|{{.Id}}|{{.State.StartedAt}}|{{.RestartCount}}','ia-chat-open-webui-1','ia-chat-searxng-1','cadvisor')
def sample():
 cg=pathlib.Path('/sys/fs/cgroup/lxc/631');mi=dict((l.split(':')[0],int(l.split()[1])*1024) for l in pathlib.Path('/proc/meminfo').read_text().splitlines() if l.startswith(('MemAvailable:','SwapTotal:','SwapFree:')))
 return {'swap_current_bytes':int((cg/'memory.swap.current').read_text()),'swap_max_bytes':int((cg/'memory.swap.max').read_text()),'memory_current_bytes':int((cg/'memory.current').read_text()),'memory_max_bytes':int((cg/'memory.max').read_text()),'events':(cg/'memory.events').read_text(),'host':mi}
old=protected();ids=identities();before=config();assert before['hostname']=='infra-webui' and before['memory']==4096
pre=sample();changed=before['swap']!=args['swap']
if args['apply'] and changed:
 backup=pathlib.Path('/root/ia-local/swap-631-backups');backup.mkdir(mode=0o700,exist_ok=True)
 data=json.dumps(before,sort_keys=True).encode();f=backup/(hashlib.sha256(data).hexdigest()+'.json')
 if not f.exists():f.write_bytes(data);f.chmod(0o600)
 subprocess.run(['pvesh','set',path,'--swap',str(args['swap']),'--digest',before['digest']],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
after=config();post=sample();assert {k:v for k,v in before.items() if k not in ['swap','digest']}=={k:v for k,v in after.items() if k not in ['swap','digest']}
assert old==protected() and ids==identities(),'Unexpected other CT change or service restart'
if args['apply']:assert after['swap']==args['swap'] and post['swap_max_bytes']==args['swap']*1024**2
with urllib.request.urlopen('http://192.168.1.66:3000/health',timeout=10) as r:assert r.status==200
print(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'ct':631,'before_swap_mib':before['swap'],'after_swap_mib':after['swap'],'desired_swap_mib':args['swap'],'configuration_writes':int(args['apply'] and changed),'before':pre,'after':post,'other_ct_configs_unchanged':True,'containers_unchanged':True,'health':200,'terraform_apply':False}))
'''
ssh=['ssh','-o','UserKnownHostsFile='+str(Path.home()/'.ssh/known_hosts'),'-o','StrictHostKeyChecking=yes','-o','BatchMode=yes','pve'];r=subprocess.run(ssh+[shlex.join(['python3','-c',code])],input=json.dumps(payload).encode(),capture_output=True,timeout=120);assert r.returncode==0,'Swap reconciliation failed; sensitive output withheld'
result=json.loads(r.stdout);dest=ROOT/'docs/roadmap/evidence/ia-chat-swap-631'/(a.label+'.json');dest.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result))
